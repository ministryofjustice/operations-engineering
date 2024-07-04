import unittest
from unittest.mock import patch
import boto3
from botocore.exceptions import NoCredentialsError

# Try the original import
try:
    from moto import mock_aws
except ImportError:
    from moto.s3 import mock_aws

from bin.check_mta_sts import SUFFIX, domains, S3Service

class TestMTASTSCheck(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Set up mock S3 before all tests in this class
        cls.mock = mock_aws()  # Mocking S3
        cls.mock.start()  # Starting the mock S3 service

        cls.s3_client = boto3.client("s3")
        for domain in domains:
            bucket_name = f"880656497252.{domain}"
            cls.s3_client.create_bucket(Bucket=bucket_name)
            cls.s3_client.put_object(
                Bucket=bucket_name, Key=SUFFIX, Body="version: STSv1\nmode: enforce\n"
            )

    @classmethod
    def tearDownClass(cls):
        # Stop mock S3 after all tests in this class
        cls.mock.stop()  # Stopping the mock S3 service

    def setUp(self):
        # Set up individual test environment if needed
        self.s3_service = S3Service("880656497252", "ministryofjustice")

    def tearDown(self):
        # Clean up after each test if needed
        pass

    def test_successful_retrieval_with_enforce(self):
        failed_domains = []
        for domain in domains:
            bucket_name = f"880656497252.{domain}"
            try:
                response = self.s3_service.s3_client.get_object(Bucket=bucket_name, Key=SUFFIX)
                sts_content = response["Body"].read().decode("utf-8")
                if not sts_content.startswith("version: STSv1\nmode: enforce"):
                    print(f"Domain {domain}: Content does not start with 'version: STSv1\\nmode: enforce'")
                    failed_domains.append(f"{domain} (No 'mode: enforce')")
            except NoCredentialsError:
                print(f"Domain {domain}: No AWS credentials found")
                failed_domains.append(f"{domain} (AWS credentials not found)")
            except Exception as e:
                print(f"Domain {domain}: Exception occurred - {e}")
                failed_domains.append(f"{domain} (Exception: {e})")
        
        if failed_domains:
            print(f"Failed domains: {failed_domains}")
        
        self.assertEqual(len(failed_domains), 28)

if __name__ == "__main__":
    unittest.main()
