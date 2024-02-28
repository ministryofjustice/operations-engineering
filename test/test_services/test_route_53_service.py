import json
import unittest
from unittest.mock import patch
from services.route_53_service import Route53Service
from moto import mock_aws
import boto3

class TestRoute53Service(unittest.TestCase):

    @mock_aws
    def setUp(self):
        self.route_53_service = Route53Service()
        self.route_53_service.client = boto3.client("route53", region_name="us-west-2")

    @mock_aws
    def test_get_route53_hosted_zones(self):
        zone = self.route_53_service.client.create_hosted_zone(Name="testdns.aws.com.", CallerReference=str(hash("foo")))

        res = self.route_53_service.get_route53_hosted_zones()

        assert res[0]['id'] == zone['HostedZone']['Id']
        assert res[0]['name'] == zone['HostedZone']['Name']

    @mock_aws
    def test_export_route53_records(self):
        zone = self.route_53_service.client.create_hosted_zone(Name="testdns.aws.com.", CallerReference=str(hash("foo")))
        self.route_53_service.client.change_resource_record_sets(
            HostedZoneId=zone['HostedZone']['Id'],
            ChangeBatch={
                "Changes": [
                    {
                        "Action": "CREATE",
                        "ResourceRecordSet": {
                            "Name": "testdns.aws.com.",
                            "Type": "MX",
                            "TTL": 1800,
                            "ResourceRecords": [
                                {"Value": "10 inbound-smtp.eu-west-1.amazonaws.com"}
                            ]
                        },
                    }
                ]
            },
        )
        self.route_53_service.client.change_resource_record_sets(
            HostedZoneId=zone['HostedZone']['Id'],
            ChangeBatch={
                "Changes": [
                    {
                        "Action": "CREATE",
                        "ResourceRecordSet": {
                            "Name": "testalias.testdns.aws.com.",
                            "Type": "A",
                            "AliasTarget": {
                                "HostedZoneId": "Z32O12XQLNTSW2",
                                "DNSName": "tribunals-nginx-1184258455.eu-west-1.elb.amazonaws.com.",
                                "EvaluateTargetHealth": False
                            }
                        },
                    }
                ]
            },
        )

        res = self.route_53_service.export_route53_records(zone['HostedZone']['Id'])
        
        assert res[0] == {'Name': 'testdns.aws.com.', 'Type': 'MX', 'TTL': 1800, 'ResourceRecords': ['10 inbound-smtp.eu-west-1.amazonaws.com']}
        assert res[1] == {'Name': 'testdns.aws.com.', 'Type': 'NS', 'TTL': 172800, 'ResourceRecords': ['ns-2048.awsdns-64.com', 'ns-2049.awsdns-65.net', 'ns-2050.awsdns-66.org', 'ns-2051.awsdns-67.co.uk']}
        assert res[2] == {'Name': 'testdns.aws.com.', 'Type': 'SOA', 'TTL': 900, 'ResourceRecords': ["{'Value': 'ns-2048.awsdns-64.com. hostmaster.example.com. 1 7200 900 1209600 86400'}"]}
        assert res[3] == {'Name': 'testalias.testdns.aws.com.', 'Type': 'A', 'AliasTarget': {'HostedZoneId': 'Z32O12XQLNTSW2', 'DNSName': 'tribunals-nginx-1184258455.eu-west-1.elb.amazonaws.com.', 'EvaluateTargetHealth': False}}

    @mock_aws
    @patch.object(Route53Service, "get_route53_hosted_zones")
    @patch.object(Route53Service, "export_route53_records")
    def test_bulk_export_route53_records(self, mock_records, mock_zone_id):

        mock_zone_id.return_value = [{"id": "/hostedzone/Z31RX3GZS94JZS", "name": "testdns.aws.com."}]
        mock_records.return_value = [
            {'Name': 'testdns.aws.com.', 'Type': 'NS', 'TTL': 172800, 'ResourceRecords': ['ns-2048.awsdns-64.com', 'ns-2049.awsdns-65.net', 'ns-2050.awsdns-66.org', 'ns-2051.awsdns-67.co.uk']}, 
            {'Name': 'testdns.aws.com.', 'Type': 'SOA', 'TTL': 900, 'ResourceRecords': ["{'Value': 'ns-2048.awsdns-64.com. hostmaster.example.com. 1 7200 900 1209600 86400'}"]}
        ]

        res = self.route_53_service.bulk_export_route53_records()

        assert json.loads(res) == {'/hostedzone/Z31RX3GZS94JZS': {'name': 'testdns.aws.com.', 'records': [{'Name': 'testdns.aws.com.', 'Type': 'NS', 'TTL': 172800, 'ResourceRecords': ['ns-2048.awsdns-64.com', 'ns-2049.awsdns-65.net', 'ns-2050.awsdns-66.org', 'ns-2051.awsdns-67.co.uk']}, {'Name': 'testdns.aws.com.', 'Type': 'SOA', 'TTL': 900, 'ResourceRecords': ["{'Value': 'ns-2048.awsdns-64.com. hostmaster.example.com. 1 7200 900 1209600 86400'}"]}]}}

    @mock_aws
    def test_check_if_hosted_zone_exists_if_true(self):
        zone = self.route_53_service.client.create_hosted_zone(Name="testdns.aws.com.", CallerReference=str(hash("foo")))
        res = self.route_53_service.check_if_hosted_zone_exists(zone['HostedZone']['Id'])
        assert res == True

    @mock_aws
    def test_check_if_hosted_zone_exists_if_false(self):
        res = self.route_53_service.check_if_hosted_zone_exists('/hostedzone/Z31RX3GZS94JZS')
        assert res == False
        
    @patch.object(Route53Service, "check_if_hosted_zone_exists")
    @mock_aws
    def test_restore_hosted_zone_if_doesnt_exist(self, mock_response):
        mock_response.return_value = False
        res = self.route_53_service.restore_hosted_zone('/hostedzone/Z31RX3GZS94JZS', 'testdns.aws.com.')
        hosted_zone_data = self.route_53_service.client.list_hosted_zones()['HostedZones']
        assert hosted_zone_data[0]['Name'] == 'testdns.aws.com.'
        assert res == hosted_zone_data[0]['Id']

    @patch.object(Route53Service, "check_if_hosted_zone_exists")
    def test_restore_hosted_zone_if_exists(self, mock_response):
        mock_response.return_value = True
        res = self.route_53_service.restore_hosted_zone('/hostedzone/Z31RX3GZS94JZS', 'testdns.aws.com.')          
        assert res == False                

    @mock_aws
    def test_check_if_record_exists_if_false(self):
        zone = self.route_53_service.client.create_hosted_zone(Name="testdns.aws.com.", CallerReference=str(hash("foo")))
        res = self.route_53_service.check_if_record_exists(zone['HostedZone']['Id'], "testdns.aws.com.", "MX")
        assert res == False

    @mock_aws
    def test_check_if_record_exists_if_true(self):
        zone = self.route_53_service.client.create_hosted_zone(Name="testdns.aws.com.", CallerReference=str(hash("foo")))
        self.route_53_service.client.change_resource_record_sets(
            HostedZoneId=zone['HostedZone']['Id'],
            ChangeBatch={
                "Changes": [
                    {
                        "Action": "CREATE",
                        "ResourceRecordSet": {
                            "Name": "testdns.aws.com.",
                            "Type": "MX",
                            "TTL": 1800,
                            "ResourceRecords": [
                                {"Value": "10 inbound-smtp.eu-west-1.amazonaws.com"}
                            ]
                        },
                    }
                ]
            },
        )

        res = self.route_53_service.check_if_record_exists(zone['HostedZone']['Id'], "testdns.aws.com.", "MX")
        assert res == True

    def test_create_change(self):
        record = {'Name': 'testdns.aws.com.', 'Type': 'MX', 'TTL': 1800, 'ResourceRecords': ['10 inbound-smtp.eu-west-1.amazonaws.com']}
        res = self.route_53_service.create_change(record)
        assert res == {'Action': 'CREATE', 'ResourceRecordSet': {'Name': 'testdns.aws.com.', 'Type': 'MX', 'TTL': 1800, 'ResourceRecords': [{'Value': '10 inbound-smtp.eu-west-1.amazonaws.com'}]}}

    @patch.object(Route53Service, "create_change")
    @patch.object(Route53Service, "check_if_record_exists")
    def test_create_change_batch_if_new_changes(self, mock_check_if_record_exists, mock_change):
        mock_check_if_record_exists.return_value = False
        mock_change.return_value = {'Action': 'CREATE', 'ResourceRecordSet': {'Name': 'testdns.aws.com.', 'Type': 'MX', 'TTL': 1800, 'ResourceRecords': [{'Value': '10 inbound-smtp.eu-west-1.amazonaws.com'}]}}
        res = self.route_53_service.create_change_batch('/hostedzone/Z31RX3GZS94JZS', [{'Name': 'test', 'Type': 'test'}])
        assert res == [{'Action': 'CREATE', 'ResourceRecordSet': {'Name': 'testdns.aws.com.', 'Type': 'MX', 'TTL': 1800, 'ResourceRecords': [{'Value': '10 inbound-smtp.eu-west-1.amazonaws.com'}]}}]

    @patch.object(Route53Service, "check_if_record_exists")
    def test_create_change_batch_if_record_exists(self, mock_check_if_record_exists):
        mock_check_if_record_exists.return_value = True
        res = self.route_53_service.create_change_batch(mock_check_if_record_exists, mock_check_if_record_exists)
        assert res == []

    @mock_aws
    @patch.object(Route53Service, "create_change_batch")
    def test_restore_hosted_zone_records_if_zone_exists(self, mock_change_batch):
        mock_change_batch.return_value = [{'Action': 'CREATE', 'ResourceRecordSet': {'Name': 'testdns.aws.com.', 'Type': 'MX', 'TTL': 1800, 'ResourceRecords': [{'Value': '10 inbound-smtp.eu-west-1.amazonaws.com'}]}}]
        zone = self.route_53_service.client.create_hosted_zone(Name="testdns.aws.com.", CallerReference=str(hash("foo")))
        self.route_53_service.restore_hosted_zone_records(zone['HostedZone']['Id'], mock_change_batch)
        res = self.route_53_service.client.list_resource_record_sets(HostedZoneId=zone['HostedZone']['Id'])['ResourceRecordSets'][0]
        assert res == {'Name': 'testdns.aws.com.', 'Type': 'MX', 'TTL': 1800, 'ResourceRecords': [{'Value': '10 inbound-smtp.eu-west-1.amazonaws.com'}]}

    @mock_aws
    def test_restore_hosted_zone_records_if_zone_doesnt_exists(self):
        res = self.route_53_service.restore_hosted_zone_records('/hostedzone/Z31RX3GZS94JZS', [])
        assert res == False

    @mock_aws
    def test_bulk_restore_hosted_zones_all(self):
        json_backup = {'/hostedzone/Z31RX3GZS94JZS': {'name': 'testdns.aws.com.', 'records': [{'Name': 'testdns.aws.com.', 'Type': 'NS', 'TTL': 172800, 'ResourceRecords': ['ns-2048.awsdns-64.com', 'ns-2049.awsdns-65.net', 'ns-2050.awsdns-66.org', 'ns-2051.awsdns-67.co.uk']}, {'Name': 'testdns.aws.com.', 'Type': 'SOA', 'TTL': 900, 'ResourceRecords': ["{'Value': 'ns-2048.awsdns-64.com. hostmaster.example.com. 1 7200 900 1209600 86400'}"]}, {'Name': 'testdns.aws.com.', 'Type': 'MX', 'TTL': 1800, 'ResourceRecords': ['10 inbound-smtp.eu-west-1.amazonaws.com']}]}}
        hosted_zones_to_restore = ["all"]
        new_zone_ids = self.route_53_service.bulk_restore_hosted_zones(json_backup, hosted_zones_to_restore)
        hz_data = self.route_53_service.client.list_hosted_zones()['HostedZones'][0]
        hz_records = self.route_53_service.client.list_resource_record_sets(HostedZoneId=new_zone_ids[0])['ResourceRecordSets']
        assert hz_data['Id'] == new_zone_ids[0]
        assert hz_data['Name'] == 'testdns.aws.com.'
        assert hz_records == [{'Name': 'testdns.aws.com.', 'Type': 'MX', 'TTL': 1800, 'ResourceRecords': [{'Value': '10 inbound-smtp.eu-west-1.amazonaws.com'}]}, {'Name': 'testdns.aws.com.', 'Type': 'NS', 'TTL': 172800, 'ResourceRecords': [{'Value': 'ns-2048.awsdns-64.com'}, {'Value': 'ns-2049.awsdns-65.net'}, {'Value': 'ns-2050.awsdns-66.org'}, {'Value': 'ns-2051.awsdns-67.co.uk'}]}, {'Name': 'testdns.aws.com.', 'Type': 'SOA', 'TTL': 900, 'ResourceRecords': [{'Value': "{'Value': 'ns-2048.awsdns-64.com. hostmaster.example.com. 1 7200 900 1209600 86400'}"}]}]

    @mock_aws
    def test_bulk_restore_hosted_zones_all(self):
        json_backup = {'/hostedzone/Z31RX3GZS94JZS': {'name': 'testdns.aws.com.', 'records': [{'Name': 'testdns.aws.com.', 'Type': 'NS', 'TTL': 172800, 'ResourceRecords': ['ns-2048.awsdns-64.com', 'ns-2049.awsdns-65.net', 'ns-2050.awsdns-66.org', 'ns-2051.awsdns-67.co.uk']}, {'Name': 'testdns.aws.com.', 'Type': 'SOA', 'TTL': 900, 'ResourceRecords': ["{'Value': 'ns-2048.awsdns-64.com. hostmaster.example.com. 1 7200 900 1209600 86400'}"]}, {'Name': 'testdns.aws.com.', 'Type': 'MX', 'TTL': 1800, 'ResourceRecords': ['10 inbound-smtp.eu-west-1.amazonaws.com']}]}}
        hosted_zones_to_restore = ['/hostedzone/Z31RX3GZS94JZS']
        new_zone_ids = self.route_53_service.bulk_restore_hosted_zones(json_backup, hosted_zones_to_restore)
        hz_data = self.route_53_service.client.list_hosted_zones()['HostedZones'][0]
        hz_records = self.route_53_service.client.list_resource_record_sets(HostedZoneId=new_zone_ids[0])['ResourceRecordSets']
        assert hz_data['Id'] == new_zone_ids[0]
        assert hz_data['Name'] == 'testdns.aws.com.'
        assert hz_records == [{'Name': 'testdns.aws.com.', 'Type': 'MX', 'TTL': 1800, 'ResourceRecords': [{'Value': '10 inbound-smtp.eu-west-1.amazonaws.com'}]}, {'Name': 'testdns.aws.com.', 'Type': 'NS', 'TTL': 172800, 'ResourceRecords': [{'Value': 'ns-2048.awsdns-64.com'}, {'Value': 'ns-2049.awsdns-65.net'}, {'Value': 'ns-2050.awsdns-66.org'}, {'Value': 'ns-2051.awsdns-67.co.uk'}]}, {'Name': 'testdns.aws.com.', 'Type': 'SOA', 'TTL': 900, 'ResourceRecords': [{'Value': "{'Value': 'ns-2048.awsdns-64.com. hostmaster.example.com. 1 7200 900 1209600 86400'}"}]}]




if __name__ == "__main__":
    unittest.main()
