import unittest
import sys
import json
from unittest.mock import patch
from bin.restore_route53_from_backup import main
from services.s3_service import S3Service
from services.route_53_service import Route53Service

class TestRestoreRoute53FromBackup(unittest.TestCase):

    @patch.object(Route53Service, "bulk_restore_hosted_zones")
    @patch.object(S3Service, "_download_file")
    def test_main_all(self, mock_download_file, mock_bulk_restore_hosted_zones):
        mock_json_data = {'/hostedzone/Z31RX3GZS94JZS': {'name': 'testdns.aws.com.', 'records': [{'Name': 'testdns.aws.com.', 'Type': 'NS', 'TTL': 172800, 'ResourceRecords': ['ns-2048.awsdns-64.com', 'ns-2049.awsdns-65.net', 'ns-2050.awsdns-66.org', 'ns-2051.awsdns-67.co.uk']}, {'Name': 'testdns.aws.com.', 'Type': 'SOA', 'TTL': 900, 'ResourceRecords': ["{'Value': 'ns-2048.awsdns-64.com. hostmaster.example.com. 1 7200 900 1209600 86400'}"]}, {'Name': 'testdns.aws.com.', 'Type': 'MX', 'TTL': 1800, 'ResourceRecords': ['10 inbound-smtp.eu-west-1.amazonaws.com']}]}}

        with open('hosted_zones.json', "w") as json_file:
            json_file.write(json.dumps(mock_json_data))

        hz_ids = ['all']

        with patch.object(sys, 'argv', ['all']):
            main()
            mock_bulk_restore_hosted_zones.assert_called_once_with(mock_json_data, hz_ids)
    
    @patch.object(Route53Service, "bulk_restore_hosted_zones")
    @patch.object(S3Service, "_download_file")
    def test_main_specified_hosted_zones(self, mock_download_file, mock_bulk_restore_hosted_zones):
        mock_json_data = {'/hostedzone/Z31RX3GZS94JZS': {'name': 'testdns.aws.com.', 'records': [{'Name': 'testdns.aws.com.', 'Type': 'NS', 'TTL': 172800, 'ResourceRecords': ['ns-2048.awsdns-64.com', 'ns-2049.awsdns-65.net', 'ns-2050.awsdns-66.org', 'ns-2051.awsdns-67.co.uk']}, {'Name': 'testdns.aws.com.', 'Type': 'SOA', 'TTL': 900, 'ResourceRecords': ["{'Value': 'ns-2048.awsdns-64.com. hostmaster.example.com. 1 7200 900 1209600 86400'}"]}, {'Name': 'testdns.aws.com.', 'Type': 'MX', 'TTL': 1800, 'ResourceRecords': ['10 inbound-smtp.eu-west-1.amazonaws.com']}]}}

        with open('hosted_zones.json', "w") as json_file:
            json_file.write(json.dumps(mock_json_data))

        hz_ids = ['hz1', 'hz2', 'hz3']

        with patch.object(sys, 'argv', ['hz1,hz2,hz3']):
            main()
            mock_bulk_restore_hosted_zones.assert_called_once_with(mock_json_data, hz_ids)

if __name__ == "__main__":
    unittest.main()
