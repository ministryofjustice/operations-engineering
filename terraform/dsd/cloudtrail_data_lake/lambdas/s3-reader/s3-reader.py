'''
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.

This is sample reference Lambda function to read GitHub Audit Log S3 file and 
pre-process before sending to CloudTrail Open Audit. 

Pre-requisites:
1) Setup GitHub Audit Log streaming to S3 
2) Setup S3 event to trigger this Lambda function on file upload

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
import io
import os
import logging
import urllib.parse
import json
import boto3
import gzip
from botocore.exceptions import ClientError
from io import BytesIO
import re

# Max payload to CloudTrail is 1 MB
MAX_FILE_SIZE = 1048576 

logger = logging.getLogger()
if 'log_level' in os.environ:
    logger.setLevel(os.environ["log_level"])
    logger.info("Log level set to %s" % logger.getEffectiveLevel())
else:
    logger.setLevel(logging.INFO)

session = boto3.Session()
s3 = session.resource("s3")
sqs = session.client("sqs")
ssm = session.client("ssm")

# Default list of allowed audit actions to sync with CloudTrail, look up from SSM parameter if available
ALLOWED_GITHUB_AUDIT_ACTIONS = [
    "repo.create*",
    "repo.change*",
    "business.set*",
    "integration.*"
    ]
try:
    if 'github_event_allow_list' in os.environ:
        ssm_response = ssm.get_parameter(
            Name=os.environ["github_event_allow_list"])["Parameter"]["Value"]
        ALLOWED_GITHUB_AUDIT_ACTIONS = ssm_response.split(",")
except Exception as err:
    logger.warning(f"Error while reading SSM parameter {os.environ['github_event_allow_list']}, using default allow-list values")
    logger.error(err)
logger.debug(f"Allowed GitHub Audit Actions : {ALLOWED_GITHUB_AUDIT_ACTIONS}")

def audit_action_filter(audit_event):
    '''
    Filter incoming GitHub audit logs for actions in the allow list
    using simple regex pattern matchine, wildcard character in front must be escaped
    return the action if match found
    '''
    logger.debug(f"Filtering action: {audit_event['action']} based on allow-list")
    for action in ALLOWED_GITHUB_AUDIT_ACTIONS:
        try:
            if re.search(action, audit_event["action"]):
                logger.debug(f"Found match of {action} for {audit_event['action']}")
                return audit_event
                break
        except Exception as err:
            logger.error(f"Regex pattern search for {action} failed and will be skipped due to {err}")
    # default to return False if no matches found
    logger.debug(f"No matches found for {audit_event['action']}")
    return False

def push_to_queue(audit_events, key):
    '''
    Send the raw filtered GitHub audit log event to SQS for further transform and ingest
    Add attributes Uid based on the file name to help creating unique Id for each event
    '''
    try:
        # sample key value: 2022/08/13/04/18/8e9d30f7-4352-43da-b197-83f8b7694ddc.json.log.gz
        gh_ingest_queue = os.environ['gh_ingest_queue']
        sqs_response = sqs.send_message(
            QueueUrl = gh_ingest_queue,
            MessageBody = json.dumps(audit_events),
            MessageAttributes = {
                "Uid": {
                    "StringValue" : key.split(".")[0].split("/")[5],
                    "DataType": "String"
                    }
                }
            )
        logger.info(f"Sent to Ingestion SQS: {gh_ingest_queue}")
    except Exception as sqsException:
        logger.error("Failed to send to Ingestion SQS: {}".format(sqsException))

def process_event_file(bucket_name, key):
    '''
    Read file from S3 bucket and validate metadata (file size, checksum, etc)
    Filter each file for allow listed GitHub Audit events and then push it to SQS 
    '''
    try:
        bucket = s3.Bucket(bucket_name)
        upload_file_size = int(
            bucket.Object(key).content_length
        )
        if upload_file_size < MAX_FILE_SIZE:  
            try:
                buffer = BytesIO(bucket.Object(key=key).get()["Body"].read())
                gzipfile = gzip.GzipFile(fileobj=buffer)
                allowed_audit_events = []
                for line in gzipfile:
                    json_object = audit_action_filter(json.loads(line))
                    if json_object:
                        logger.debug(json_object)
                        allowed_audit_events.append(json_object)
                if len(allowed_audit_events) > 0:
                    push_to_queue(allowed_audit_events, key)
                else:
                    logger.info("No matched events found, skipped")
            except Exception as err:
                logger.error(f"Error while reading object {key} from bucket {bucket_name} : {err}")
                raise err
        else:
            logger.error(f"File ({key}) exceeds maximum file scan size ({MAX_FILE_SIZE} bytes), skipped.")
    except Exception as handlerException:
        logger.error(handlerException)
        return False
        
def lambda_handler(event, context): 
    '''
    Assume each event raised by single S3 file upload
    Process each file, filter and then push it to queue for tranform + ingest
    '''
    logger.debug(json.dumps(event))
    bucket_name = event["Records"][0]["s3"]["bucket"]["name"]
    key = urllib.parse.unquote_plus(event["Records"][0]["s3"]["object"]["key"], encoding="utf-8")
    process_event_file(bucket_name, key)
    