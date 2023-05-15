import os
import json
import sys
import traceback
import boto3


def create_delete_cname_record(cname):
    """Create a delete cname record
    Args:
        cname (string): The cname record from AWS.
    Returns:
        (dict): a completed delete cname record
    """
    return {
        "Action": "DELETE",
        "ResourceRecordSet": {
            "Name": cname["Name"],
            "Type": "CNAME",
            "TTL": cname["TTL"],
            "ResourceRecords": [{"Value": cname["ResourceRecords"][0]["Value"]}],
        },
    }


def get_cname_records_to_delete(route53_client, hosted_zone_id):
    """Find which cname records can be deleted

    Args:
        route53_client (BaseClient)
        hosted_zone_id (string): The id of the hosted zone

    Returns:
        list[cname_record]: a list of delete cname records to be deleted
    """
    records_to_delete = []
    next_record_name = "a"
    next_record_type = "CNAME"
    next_record_id = "0"

    while True:
        response = route53_client.list_resource_record_sets(
            HostedZoneId=hosted_zone_id,
            StartRecordName=next_record_name,
            StartRecordType=next_record_type,
            StartRecordIdentifier=next_record_id,
            MaxItems="400",
        )

        for record_set in response["ResourceRecordSets"]:
            if record_set["Type"] == "CNAME" and (
                "comodoca" in record_set["ResourceRecords"][0]["Value"] or
                "sectigo" in record_set["ResourceRecords"][0]["Value"]
            ):
                delete_record = create_delete_cname_record(record_set)
                records_to_delete.append(delete_record)

        if response["IsTruncated"]:
            next_record_name = response["NextRecordName"]
            next_record_id = response["NextRecordIdentifier"]
        else:
            break

    return records_to_delete


def delete_cname_records(route53_client, records_to_delete, hosted_zone_id):
    """Delete selected cname records from the AWS Route53 host zone

    Args:
        route53_client (BaseClient)
        records_to_delete (list[dict]) the list of cname records to delete
        hosted_zone_id (string): The id of the hosted zone
    """
    if len(records_to_delete) != 0:
        print(json.dumps(records_to_delete, indent=2))
        # response = route53_client.change_resource_record_sets(
        #     ChangeBatch={"Changes": records_to_delete},
        #     HostedZoneId=hosted_zone_id,
        # )
        # if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
        #     print("Deleted records:")
        #     print(json.dumps(records_to_delete, indent=2))


def get_hosted_zone_id(zone_name):
    hosted_zone_id = os.getenv(zone_name)
    if not hosted_zone_id:
        raise ValueError(f"The env variable {zone_name} is empty or missing")
    return hosted_zone_id


def main():
    print("Start")

    route53_client = boto3.client("route53")

    host_zone_id_1 = get_hosted_zone_id("HOSTED_ZONE_1")
    host_zone_id_2 = get_hosted_zone_id("HOSTED_ZONE_2")

    records_to_delete = get_cname_records_to_delete(route53_client, host_zone_id_1)
    delete_cname_records(route53_client, records_to_delete, host_zone_id_1)

    records_to_delete = get_cname_records_to_delete(route53_client, host_zone_id_2)
    delete_cname_records(route53_client, records_to_delete, host_zone_id_2)

    print("Finished")


if __name__ == "__main__":
    main()
