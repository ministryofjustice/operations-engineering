import os
import boto3
import json
import sys
import traceback

from botocore.client import BaseClient


def print_stack_trace(message):
    """This will attempt to print a stack trace when an exception occurs
    Args:
        message (string): A message to print when exception occurs
    """
    print(message)
    try:
        exc_info = sys.exc_info()
    finally:
        traceback.print_exception(*exc_info)
        del exc_info


def create_delete_cname_record(cname):
    """Create a delete cname record
    Args:
        cname (string): The cname record from AWS.
    Returns:
        cname_record: a completed delete cname record
    """
    cname_record = {
        "Action": "DELETE",
        "ResourceRecordSet": {
            "Name": cname["Name"],
            "Type": "CNAME",
            "TTL": cname["TTL"],
            "ResourceRecords": [{"Value": cname["ResourceRecords"][0]["Value"]}],
        },
    }

    return cname_record


def delete_cname_records(route53_client: BaseClient, host_zone_id):
    """Delete selected cname records from the AWS Route53 host zone

    Args:
        host_zone_id (string): The AWS ID of the host zone that contains the records to delete
        route53_client (BaseClient)
    """
    delete_records = []
    next_record_name = "a"
    next_record_type = "CNAME"

    while next_record_name is not None and next_record_type is not None:
        try:
            response = route53_client.list_resource_record_sets(
                HostedZoneId=host_zone_id,
                StartRecordName=next_record_name,
                StartRecordType=next_record_type,
                MaxItems="400",
            )

            for record_set in response["ResourceRecordSets"]:
                if record_set["Type"] == "CNAME":
                    if (
                        "comodoca" in record_set["ResourceRecords"][0]["Value"]
                        or "sectigo" in record_set["ResourceRecords"][0]["Value"]
                    ):
                        delete_record = create_delete_cname_record(record_set)
                        delete_records.append(delete_record)

            next_record_name = response["NextRecordName"]
            next_record_type = response["NextRecordType"]

        except BaseException as err:
            print(err)
            next_record_name = None
            next_record_type = None

    try:
        if len(delete_records) != 0:
            response = route53_client.change_resource_record_sets(
                ChangeBatch={"Changes": delete_records},
                HostedZoneId=host_zone_id,
            )
            print(response)

            print("Deleted records:")
            print(json.dumps(delete_records, indent=2))
    except BaseException as err:
        print(err)
        print_stack_trace("Exception: AWS call to delete cname records")


def main():
    try:
        route53_client = boto3.client("route53")
    except BaseException as err:
        print(err)
        print_stack_trace("Exception: Problem with the route53 client.")

    hosted_zone_1 = os.getenv("HOSTED_ZONE_1")
    if not hosted_zone_1:
        raise ValueError(
            "The env variable HOSTED_ZONE_1 is empty or missing")

    hosted_zone_2 = os.getenv("HOSTED_ZONE_2")
    if not hosted_zone_2:
        raise ValueError(
            "The env variable HOSTED_ZONE_2 is empty or missing")

    print("Start")
    delete_cname_records(route53_client, hosted_zone_1)
    delete_cname_records(route53_client, hosted_zone_2)
    print("Finished")


if __name__ == "__main__":
    main()
