'''
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.

This is sample reference Lambda function to transform GitHub Audit Log events
into AWS CloudTrail Audit Event format

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
import json
import logging
import boto3
import os
import traceback
from datetime import datetime
from botocore.exceptions import ClientError

logger = logging.getLogger()
if 'log_level' in os.environ:
    logger.setLevel(os.environ["log_level"])
    logger.info("Log level set to %s" % logger.getEffectiveLevel())
else:
    logger.setLevel(logging.INFO)

session = boto3.Session()
s3 = session.resource("s3")
sqs = session.client("sqs")
sts = session.client('sts')
ssm = session.client("ssm")
cloudtrail_open_audit = session.client('cloudtrail-data')
RECIPIENT_ACCOUNT_ID = sts.get_caller_identity()['Account']

try:
    if 'github_cloudtrail_channel' in os.environ:
        CLOUDTRAIL_LAKE_CHANNEL_ARN = ssm.get_parameter(
            Name=os.environ["github_cloudtrail_channel"])["Parameter"]["Value"]
except Exception as err:
    logger.error(f"Error while reading SSM parameter {os.environ['github_cloudtrail_channel']}, no CloudTrail Lake channel Arn defined, unable to continue")
    logger.error(err)
    raise err
logger.debug(f"CloudTrail Lake Channel Arn: {CLOUDTRAIL_LAKE_CHANNEL_ARN}")

if 'github_event_version' in os.environ:
    GITHUB_EVENT_VERSION = os.environ["github_event_version"]
    logger.info(f"GITHUB_EVENT_VERSION set to : {GITHUB_EVENT_VERSION}")
else:
    GITHUB_EVENT_VERSION = "0"

if 'github_user_type' in os.environ:
    GITHUB_USER_TYPE = os.environ["github_user_type"]
    logger.info(f"GITHUB_USER_TYPE set to : {GITHUB_USER_TYPE}")
else:
    GITHUB_USER_TYPE = "user"

if 'github_event_source' in os.environ:
    GITHUB_EVENT_SOURCE = os.environ["github_event_source"]
    logger.info(f"GITHUB_EVENT_SOURCE set to : {GITHUB_EVENT_SOURCE}")
else:
    GITHUB_EVENT_SOURCE = "github.audit.streaming"

if 'github_transform_dlq' in os.environ:
    GITHUB_TRANSFORM_DLQ = os.environ["github_transform_dlq"]
    logger.info(f"GITHUB_TRANSFORM_DLQ set to : {GITHUB_TRANSFORM_DLQ}")
else:
    GITHUB_TRANSFORM_DLQ = False

def transform_event(record):
    '''
    Transform incoming GitHub Audit Log event into CloudTrail Open Audit format
    GitHub Audit Log event format / schema differs per each type of actions 
    most common attributes are mapped to all required CloudTrail Open Audit attributes
    remaining unused attributes are added as optional `requestParameters`
    Returns the transformed event data in CloudTrail Open Audit format
    '''
    logger.debug(f"Transforming record: {record}")

    # principalId
    try:
        principalId = record["actor"]
        record.pop("actor")
    except:
        principalId = record["business"]
        record.pop("business")
    
    # userIdentity.details
    userIdentityDetails = {}
    try:
        userIdentityDetails["GitHubOrganization"] = record["org"]
        record.pop("org")
    except:
        userIdentityDetails["GitHubOrganization"] = "none"

    try:
        userIdentityDetails["Repository"] = record["repo"]
        record.pop("repo")
    except:
        userIdentityDetails["Repository"] = "none"

    try:
        userIdentityDetails["Location"] = record["actor_location"]
        record.pop("actor_location")
    except:
        userIdentityDetails["Location"] = "none"
    
    # eventName
    try:
        eventName = record["action"]
        record.pop("action")
    except:
        eventName = "Unknown"
    
    # UID
    UID = record["_document_id"]
    record.pop("_document_id")
    
    # eventTime
    eventTime = record["@timestamp"]
    record.pop("@timestamp")
    
    # Remove unrelevant data and store all other unused attributes to `requestParameters`
    record.pop("created_at", "not-found")

    eventData = {
        "version" : GITHUB_EVENT_VERSION,
        "userIdentity" : {
            "type": GITHUB_USER_TYPE,
            "principalId" : principalId,
            "details" : userIdentityDetails
        },
        "eventSource" : GITHUB_EVENT_SOURCE,
        "eventName" : eventName,
        "eventTime" : datetime.utcfromtimestamp(int(eventTime/1000)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "UID" : UID,
        "requestParameters" : record,
        "recipientAccountId" : RECIPIENT_ACCOUNT_ID
    }
    logger.debug(json.dumps(eventData))
    return eventData

def generate_audit_events_payload(audit_events, event_id):
    '''
    Process batch of GitHub Audit Log events into single payload to CloudTrail
    Returns the formatted payload
    '''
    auditEvents = []
    counter = 1
    for event in audit_events:
        auditEvents.append(
            {
                "eventData": json.dumps(event), 
                "id": event_id + "_" + str(counter) # GitHub '_document_id' does not match the 'id' schema, so we use the file-name + counter 
            }
        )
        counter += 1    #single s3 object may contain multiple actions, hence we add counter for unique id
            
    audit_events_payload = {
        "auditEvents": auditEvents
    }
    return audit_events_payload

def ingest_event(t_event):
    '''
    Send the payload to CloudTrail Open Audit endpoint
    Return the API response
    '''
    result = True
    try:
        output = cloudtrail_open_audit.put_audit_events(
            auditEvents=t_event["auditEvents"],
            channelArn=CLOUDTRAIL_LAKE_CHANNEL_ARN)
        failed = output["failed"]
        if len(failed) > 0:
            logger.error("Failed to ingest event: %s", failed)
            result = False
        else:
            logger.info("Event successfully ingested: %s", output["successful"])

    except ClientError as cloudtrailException:
        logger.error("Failed to ingest event: %s", str(cloudtrailException))
        raise cloudtrailException

    return result

def send_to_dql(payload, unique_id):
    '''
    Optional FIFO DLQ to inspect payload sent to CloudTrail
    '''
    if GITHUB_TRANSFORM_DLQ:
        try:
            sqs_response = sqs.send_message(
                QueueUrl=GITHUB_TRANSFORM_DLQ,
                MessageBody=json.dumps(payload),
                MessageDeduplicationId=unique_id,
                MessageGroupId="payload_redrive"
                )
            logger.warning(f"Unprocessed event sent to DQL: {sqs_response}")
        except Exception as sqsException:
            logger.error(f"Failed to send to DLQ: {sqsException}")
        return True
    else:
        logger.warning("No DLQ available, please setup env var GITHUB_TRANSFORM_DLQ, message is lost forever")
        return False
    
def lambda_handler(event, context):
    '''
    Lambda may process up to N number of filtered records and batch it to CloudTrail as single API call
    # TODO: 
    # 1) batch max of 100 actions, 1 MB per API call
    # 2) batch smaller item and re-generate new Uid    
    '''
    logger.debug(boto3.__version__)
    logger.debug(json.dumps(event))

    for record in event["Records"]:
        audit_events = []
        for action in json.loads(record["body"]):
            audit_events.append(transform_event(action))
        try:            
            payload = generate_audit_events_payload(audit_events, record["messageAttributes"]["Uid"]["stringValue"])
            logger.debug(json.dumps(payload))
            results = ingest_event(payload)
        except Exception as err:
            traceback.print_exc()
            logger.error("Error processing paylod, sending to DQL")
            send_to_dql(payload, record["messageAttributes"]["Uid"]["stringValue"])
            raise err