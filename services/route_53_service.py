import boto3
import json
from datetime import datetime


class Route53Service:
    def __init__(self) -> None:
        self.client = boto3.client("route53")

    def get_route53_hosted_zones(self):

        response = self.client.list_hosted_zones()

        hosted_zone_ids = [zone['Id'] for zone in response['HostedZones']]

        return hosted_zone_ids
    
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

        return json.dumps(records, indent=4)
    
    def bulk_export_route53_records(self):

        hosted_zone_ids = self.get_route53_hosted_zones()

        exported_records = {}

        for zone_id in hosted_zone_ids:
            records = self.export_route53_records(zone_id)
            exported_records[zone_id] = records

        return json.dumps(exported_records, indent=4)