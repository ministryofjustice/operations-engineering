import json
import os 
import unittest
from unittest.mock import patch
from bin.route53_backup import main
from services.route_53_service import Route53Service
from services.s3_service import S3Service


class TestExportRoute53(unittest.TestCase):

    @patch.object(S3Service, "save_r53_backup_file")
    @patch.object(Route53Service, "bulk_export_route53_records")
    def test_main(self, mock_records, mock_save_r53_backup_file):
        records = {'/hostedzone/Z31RX3GZS94JZS': 
            [
                {'Name': 'testdns.aws.com.', 'Type': 'NS', 'TTL': 172800, 'ResourceRecords': ['ns-2048.awsdns-64.com', 'ns-2049.awsdns-65.net', 'ns-2050.awsdns-66.org', 'ns-2051.awsdns-67.co.uk']}, 
                {'Name': 'testdns.aws.com.', 'Type': 'SOA', 'TTL': 900, 'ResourceRecords': ["{'Value': 'ns-2048.awsdns-64.com. hostmaster.example.com. 1 7200 900 1209600 86400'}"]}
            ]
        }
        mock_records.return_value = json.dumps(records)

        main()

        file = open('hosted_zones.json')

        res = json.load(file)

        file.close()

        os.remove("hosted_zones.json")

        assert records == res
        mock_save_r53_backup_file.assert_called_once()


if __name__ == "__main__":
    unittest.main()
