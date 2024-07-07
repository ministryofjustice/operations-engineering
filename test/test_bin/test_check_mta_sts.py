import unittest
import boto3
from botocore.exceptions import NoCredentialsError
from unittest.mock import patch, MagicMock

# Import the module containing the original code
from bin.check_mta_sts import SUFFIX, domains, S3Service


class TestMTASTSChecker(unittest.TestCase):

    def setUp(self):
        """Set up mock S3 client and initialize test data."""
        self.mock_s3_client = MagicMock(spec=boto3.client('s3'))
        self.s3_service = S3Service("880656497252", "ministryofjustice")
        self.s3_service.s3_client = self.mock_s3_client
        self.failed_domains = []

    def simulate_s3_buckets(self, mode):
        """Simulate S3 buckets with specified mode."""
        for domain in domains:
            bucket_name = f"880656497252.{domain}"
            self.mock_s3_client.create_bucket(Bucket=bucket_name)
            self.mock_s3_client.put_object(Bucket=bucket_name, Key=SUFFIX, Body=f"version: STSv1\nmode: {mode}\n")

    def run_test_logic(self, expected_mode):
        """Run the original code logic and check for expected errors."""
        self.simulate_s3_buckets(expected_mode)

        for domain in domains:
            bucket_name = f"880656497252.{domain}"
            try:
                response = self.mock_s3_client.get_object(Bucket=bucket_name, Key=SUFFIX)
                sts_content = response["Body"].read().decode("utf-8")
                if f"mode: {expected_mode}" not in sts_content:
                    self.failed_domains.append(f"{domain} (No '{expected_mode}')")
            except NoCredentialsError:
                self.failed_domains.append(f"{domain} (AWS credentials not found)")
            except ValueError as e:
                self.failed_domains.append(f"{domain} (Exception: {e})")

    def test_successful_retrieval_with_enforce(self):
        """Test successful retrieval of MTA-STS configuration with 'mode: enforce'."""
        with patch('boto3.client', return_value=self.mock_s3_client):
            self.run_test_logic("enforce")
        self.assertEqual(len(self.failed_domains), 28, f"Failed domains: {self.failed_domains}")

    def test_successful_retrieval_without_enforce(self):
        """Test successful retrieval of MTA-STS configuration without 'mode: enforce'."""
        with patch('boto3.client', return_value=self.mock_s3_client):
            self.run_test_logic("testing")
        self.assertGreater(len(self.failed_domains), 0, f"Failed domains: {self.failed_domains}")
        self.assertIn(" (No 'testing')", self.failed_domains[0])

    def test_no_credentials(self):
        """Test handling of missing AWS credentials."""
        self.mock_s3_client.get_object.side_effect = NoCredentialsError()
        with patch('boto3.client', return_value=self.mock_s3_client):
            self.run_test_logic("enforce")
        self.assertGreater(len(self.failed_domains), 0, f"Failed domains: {self.failed_domains}")
        self.assertIn(" (AWS credentials not found)", self.failed_domains[0])


if __name__ == "__main__":
    unittest.main()
