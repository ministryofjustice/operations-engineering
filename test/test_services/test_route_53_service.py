import json
import unittest
from unittest.mock import patch
import boto3
from moto import mock_aws
from services.route_53_service import Route53Service


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

    def test_create_delete_cname_record(self):
        cname_input = {
            "Name": "abc",
            "Type": "CNAME",
            "TTL": 123,
            "ResourceRecords": [
                {
                    "Value": "cname_value_comodoca"
                }
            ]
        }

        expected_cname_to_delete = {
            "Action": "DELETE",
            "ResourceRecordSet": {
                "Name": "abc",
                "Type": "CNAME",
                "TTL": 123,
                "ResourceRecords": [{"Value": "cname_value_comodoca"}],
            },
        }

        self.assertEqual(self.route_53_service.create_delete_cname_request(cname_input), expected_cname_to_delete)

    @mock_aws
    def test_get_cname_records_to_delete_with_pagination_with_no_cname_records(self):
        zone = self.route_53_service.client.create_hosted_zone(Name="testdns.aws.com.", CallerReference=str(hash("foo")))

        self.assertEqual(self.route_53_service.get_cname_records_to_delete(zone['HostedZone']['Id']), [])

    @mock_aws
    def test_get_cname_records_to_delete_with_pagination_when_cname_records_exist_but_not_ours(self):
        zone = self.route_53_service.client.create_hosted_zone(Name="testdns.aws.com.", CallerReference=str(hash("foo")))
        self.route_53_service.client.change_resource_record_sets(
            HostedZoneId=zone['HostedZone']['Id'],
            ChangeBatch={
                "Changes": [
                    {
                        "Action": "CREATE",
                        "ResourceRecordSet": {
                            "Name": "testdns.aws.com.",
                            "TTL": 300,
                            "Type": "CNAME",
                            "ResourceRecords": [
                                {"Value": "some_cname_value"}
                            ]
                        },
                    }
                ]
            },
        )

        self.assertEqual(self.route_53_service.get_cname_records_to_delete(zone['HostedZone']['Id']), [])

    @mock_aws
    def test_get_cname_records_to_delete_with_pagination_when_cname_records_exist(self):
        zone = self.route_53_service.client.create_hosted_zone(Name="testdns.aws.com.", CallerReference=str(hash("foo")))
        self.route_53_service.client.change_resource_record_sets(
            HostedZoneId=zone['HostedZone']['Id'],
            ChangeBatch={
                "Changes": [
                    {
                        "Action": "CREATE",
                        "ResourceRecordSet": {
                            "Name": "testdns.aws.com.",
                            "TTL": 300,
                            "Type": "CNAME",
                            "ResourceRecords": [
                                {"Value": "cname_value_comodoca"}
                            ]
                        },
                    },
                    {
                        "Action": "CREATE",
                        "ResourceRecordSet": {
                            "Name": "testdns.aws.com.",
                            "TTL": 300,
                            "Type": "CNAME",
                            "ResourceRecords": [
                                {"Value": "cname_value_sectigo"}
                            ]
                        },
                    }

                ]
            },
        )

        records_to_delete = self.route_53_service.get_cname_records_to_delete(zone['HostedZone']['Id'])
        self.assertEqual(len(records_to_delete), 2)

    @mock_aws
    def test_delete_cname_records(self):
        zone = self.route_53_service.client.create_hosted_zone(Name="testdns.aws.com.", CallerReference=str(hash("foo")))
        self.route_53_service.client.change_resource_record_sets(
            HostedZoneId=zone['HostedZone']['Id'],
            ChangeBatch={
                "Changes": [
                    {
                        "Action": "CREATE",
                        "ResourceRecordSet": {
                            "Name": "testdns.aws.com.",
                            "Type": "CNAME",
                            "TTL": 300,
                            "ResourceRecords": [
                                {"Value": "cname_value_comodoca"}
                            ]
                        },
                    },
                    {
                        "Action": "CREATE",
                        "ResourceRecordSet": {
                            "Name": "testdns.aws.com.",
                            "Type": "CNAME",
                            "TTL": 300,
                            "ResourceRecords": [
                                {"Value": "cname_value_sectigo"}
                            ]
                        },
                    }

                ]
            },
        )

        self.route_53_service.delete_cname_records(zone['HostedZone']['Id'])

        self.assertEqual(list(filter(lambda record_set: record_set["Type"] == "CNAME", self.route_53_service.client.list_resource_record_sets(HostedZoneId=zone['HostedZone']['Id'])["ResourceRecordSets"])), [])


if __name__ == "__main__":
    unittest.main()
