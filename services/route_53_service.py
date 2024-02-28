import boto3
import json


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
    
    def check_if_hosted_zone_exists(self, hosted_zone_id):
        try:
            self.client.get_hosted_zone(Id=hosted_zone_id)
            print(f"Hosted zone '{hosted_zone_id}' already exists.")
            return True
        except self.client.exceptions.NoSuchHostedZone:
            print(f"Hosted zone '{hosted_zone_id}' doesn't exist.")
            return False
    
    def restore_hosted_zone(self, hosted_zone_id, hosted_zone_name):
        if not self.check_if_hosted_zone_exists(hosted_zone_id):
            caller_reference = str(hash(hosted_zone_id))
            zone = self.client.create_hosted_zone(Name=hosted_zone_name, CallerReference=caller_reference)
            print(f"Created hosted zone '{hosted_zone_name}'.")
            return zone['HostedZone']['Id']
        else:
            print(f"A hosted zone with id '{hosted_zone_id}' already exists")
            return False
        
    def check_if_record_exists(self, hosted_zone_id, record_name, record_type):
        records = self.client.list_resource_record_sets(HostedZoneId=hosted_zone_id)['ResourceRecordSets']
        for record in records:
            if record["Name"] == record_name and record["Type"] == record_type:
                print(f"Resource record '{record_name}' of type '{record_type}' already exists.")
                return True
        return False
    
    def create_change(self, record):
        change = {
            'Action': 'CREATE',
            'ResourceRecordSet': {
                'Name': record['Name'],
                'Type': record['Type'],
                'TTL': record['TTL'],
            }
        }

        if 'ResourceRecords' in record:
            change['ResourceRecordSet']['ResourceRecords'] = [{'Value': value} for value in record['ResourceRecords']]
        elif 'AliasTarget' in record:
            change['ResourceRecordSet']['AliasTarget'] = record['AliasTarget']

        return change

    def create_change_batch(self, hosted_zone_id, records):
        changes = []
        for record in records:
            if not self.check_if_record_exists(hosted_zone_id, record['Name'], record['Type']):
                change = self.create_change(record)
                changes.append(change)
        return changes
    
    def restore_hosted_zone_records(self, hosted_zone_id, records):
        if not self.check_if_hosted_zone_exists(hosted_zone_id):
            return False
        
        changes = self.create_change_batch(hosted_zone_id, records)
        response = self.client.change_resource_record_sets(
            HostedZoneId=hosted_zone_id,
            ChangeBatch={
                'Changes': changes
            }
        )
        print("Hosted zone records restored successfully.")
        print("Change info:", response)

    def bulk_restore_hosted_zones(self, json_backup, hosted_zones_to_restore):

        backup_data = json_backup

        new_zone_ids = []

        if hosted_zones_to_restore == ['all']:
            for hz_id in backup_data.keys():
                new_zone_id = self.restore_hosted_zone(hz_id, backup_data[hz_id]['name'])
                self.restore_hosted_zone_records(new_zone_id, backup_data[hz_id]['records'])
                new_zone_ids.append(new_zone_id)
        else:
            for hz_id in hosted_zones_to_restore:
                if hz_id in backup_data.keys():
                    new_zone_id = self.restore_hosted_zone(hz_id, backup_data[hz_id]['name'])
                    self.restore_hosted_zone_records(new_zone_id, backup_data[hz_id]['records'])
                    new_zone_ids.append(new_zone_id)
        
        return new_zone_ids