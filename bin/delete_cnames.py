import sys
import json
import boto3


def create_delete_cname_request(cname):
    """Create a delete cname change request
    Args:
        cname (string): The cname record from AWS.
    Returns:
        (dict): a completed delete cname request
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
        list[cname_record]: a list of cname records eligible for deletion
    """
    records_to_delete = []
    next_record_name = "a"
    next_record_type = "CNAME"

    while True:
        response = route53_client.list_resource_record_sets(
            HostedZoneId=hosted_zone_id,
            StartRecordName=next_record_name,
            StartRecordType=next_record_type,
            MaxItems="400",
        )

        for record_set in response["ResourceRecordSets"]:
            if record_set["Type"] == "CNAME" and (
                "comodoca" in record_set["ResourceRecords"][0]["Value"] or
                "sectigo" in record_set["ResourceRecords"][0]["Value"]
            ):
                delete_record = create_delete_cname_request(record_set)
                records_to_delete.append(delete_record)

        if response["IsTruncated"]:
            next_record_name = response["NextRecordName"]
        else:
            break

    return records_to_delete


def delete_cname_records(route53_client, records_to_delete, hosted_zone_id):
    """Delete selected cname records from the AWS Route53 hosted zone
    Args:
        route53_client (BaseClient)
        records_to_delete (list[dict]) the list of cname records to delete
        hosted_zone_id (string): The id of the hosted zone
    """
    if len(records_to_delete) != 0:
        response = route53_client.change_resource_record_sets(
            ChangeBatch={"Changes": records_to_delete},
            HostedZoneId=hosted_zone_id,
        )
        if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
            print("Deleted records:")
            print(json.dumps(records_to_delete, indent=2))


def main():
    print("Start")

    if len(sys.argv) < 1:
        raise ValueError(f"Please specify hosted zones as CLI arguments")

    route53_client = boto3.client("route53")

    hosted_zones = sys.argv

    for zone in hosted_zones:
        records_to_delete = get_cname_records_to_delete(route53_client, zone)
        delete_cname_records(route53_client, records_to_delete, zone)

    print("Finished")


if __name__ == "__main__":
    main()
