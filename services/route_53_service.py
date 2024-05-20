import json
import boto3


class Route53Service:
    def __init__(self) -> None:
        self.client = boto3.client("route53")

    def get_route53_hosted_zones(self):

        response = self.client.list_hosted_zones()

        hosted_zone_data = []
        for zone in response['HostedZones']:
            hosted_zone_data.append({'id': zone['Id'], 'name': zone['Name']})

        return hosted_zone_data

    def export_route53_records(self, zone_id: str):

        response = self.client.list_resource_record_sets(HostedZoneId=zone_id)

        records = []

        for record_set in response['ResourceRecordSets']:
            record = None
            if "ResourceRecords" in record_set:
                record = {
                    "Name": record_set['Name'],
                    "Type": record_set['Type'],
                    "TTL": record_set['TTL'],
                    "ResourceRecords": [record['Value'] for record in record_set.get('ResourceRecords', [])],
                }
            else:
                record = {
                    "Name": record_set['Name'],
                    "Type": record_set['Type'],
                    'AliasTarget': record_set['AliasTarget']
                }
            records.append(record)

        return records

    def bulk_export_route53_records(self):

        hosted_zone_data = self.get_route53_hosted_zones()

        exported_records = {}

        for zone in hosted_zone_data:
            records = self.export_route53_records(zone['id'])
            exported_records[zone['id']] = {'name': zone['name'], 'records': records}

        return json.dumps(exported_records, indent=4)

    def create_delete_cname_request(cname):
        return {
            "Action": "DELETE",
            "ResourceRecordSet": {
                "Name": cname["Name"],
                "Type": "CNAME",
                "TTL": cname["TTL"],
                "ResourceRecords": [{"Value": cname["ResourceRecords"][0]["Value"]}],
            },
        }


    def get_cname_records_to_delete(self, hosted_zone_id):
        records_to_delete = []
        next_record_name = "a"
        next_record_type = "CNAME"

        while True:
            response = self.client.list_resource_record_sets(
                HostedZoneId=hosted_zone_id,
                StartRecordName=next_record_name,
                StartRecordType=next_record_type,
                MaxItems="300",
            )

            for record_set in response["ResourceRecordSets"]:
                if record_set["Type"] == "CNAME" and (
                    "comodoca" in record_set["ResourceRecords"][0]["Value"] or
                    "sectigo" in record_set["ResourceRecords"][0]["Value"]
                ):
                    delete_record = self.create_delete_cname_request(record_set)
                    records_to_delete.append(delete_record)

            if response["IsTruncated"]:
                next_record_name = response["NextRecordName"]
            else:
                break

        return records_to_delete

    def delete_cname_records(self, hosted_zone_id):
        records_to_delete = self.get_cname_records_to_delete(hosted_zone_id)

        if len(records_to_delete) != 0:
            response = self.client.change_resource_record_sets(
                ChangeBatch={"Changes": records_to_delete},
                HostedZoneId=hosted_zone_id,
            )
            if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
                print("Deleted records:")
                print(json.dumps(records_to_delete, indent=2))
        else:
            print('No cname records to delete')
