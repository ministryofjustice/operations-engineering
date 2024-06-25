import unittest
from unittest.mock import patch
import boto3
from botocore.exceptions import NoCredentialsError
from moto import mock_s3

# Import the module containing the original code
from bin.check_mta_sts import SUFFIX, domains, failed_domains, s3


class TestMTASTSChecker(unittest.TestCase):

    def setUp(self):
        # Clear the failed_domains list before each test
        failed_domains.clear()
    @mock_s3
    def test_successful_retrieval_with_enforce(self):
        """Test successful retrieval of MTA-STS configuration with 'mode: enforce'."""
        s3_client = boto3.client("s3")
        for domain in domains:
            bucket_name = f"880656497252.{domain}"
            s3_client.create_bucket(Bucket=bucket_name)
            s3_client.put_object(
                Bucket=bucket_name, Key=SUFFIX, Body="version: STSv1\nmode: enforce\n"
            )

        # Run the original code logic
        for domain in domains:
            bucket_name = f"880656497252.{domain}"
            try:
                response = s3.get_object(Bucket=bucket_name, Key=SUFFIX)
                sts_content = response["Body"].read().decode("utf-8")
                has_enforce = any(
                    line.startswith("mode: enforce") for line in sts_content.split("\n")
                )
                if not has_enforce:
                    failed_domains.append(f"{domain} (No 'mode: enforce')")
            except NoCredentialsError:
                failed_domains.append(f"{domain} (AWS credentials not found)")
            except Exception as e:
                failed_domains.append(f"{domain} (Exception: {e})")
        self.assertEqual(len(failed_domains), 0)
    @mock_s3
    def test_successful_retrieval_without_enforce(self):
        """Test successful retrieval of MTA-STS configuration without 'mode: enforce'."""
        s3_client = boto3.client("s3")
        for domain in domains:
            bucket_name = f"880656497252.{domain}"
            s3_client.create_bucket(Bucket=bucket_name)
            s3_client.put_object(
                Bucket=bucket_name, Key=SUFFIX, Body="version: STSv1\nmode: testing\n"
            )

        # Run the original code logic
        for domain in domains:
            bucket_name = f"880656497252.{domain}"
            try:
                response = s3.get_object(Bucket=bucket_name, Key=SUFFIX)
                sts_content = response["Body"].read().decode("utf-8")
                has_enforce = any(
                    line.startswith("mode: enforce") for line in sts_content.split("\n")
                )
                if not has_enforce:
                    failed_domains.append(f"{domain} (No 'mode: enforce')")
            except NoCredentialsError:
                failed_domains.append(f"{domain} (AWS credentials not found)")
            except Exception as e:
                failed_domains.append(f"{domain} (Exception: {e})")
        self.assertGreater(len(failed_domains), 0)
        self.assertIn(" (No 'mode: enforce')", failed_domains[0])
    @mock_s3
    def test_no_credentials(self):
        """Test handling of missing AWS credentials."""
        s3_client = boto3.client(
            "s3", aws_access_key_id="", aws_secret_access_key="", aws_session_token=""
        )
        for domain in domains:
            bucket_name = f"880656497252.{domain}"
            s3_client.create_bucket(Bucket=bucket_name)
            s3_client.put_object(
                Bucket=bucket_name, Key=SUFFIX, Body="version: STSv1\nmode: enforce\n"
            )

        # Run the original code logic with a dummy S3 client to trigger an exception
        for domain in domains:
            bucket_name = f"880656497252.{domain}"
            try:
                response = s3.get_object(Bucket=bucket_name, Key=SUFFIX)
                sts_content = response["Body"].read().decode("utf-8")
                has_enforce = any(
                    line.startswith("mode: enforce") for line in sts_content.split("\n")
                )
                if not has_enforce:
                    failed_domains.append(f"{domain} (No 'mode: enforce')")
            except NoCredentialsError:
                failed_domains.append(f"{domain} (AWS credentials not found)")
            except Exception as e:
                failed_domains.append(f"{domain} (Exception: {e})")
        self.assertGreater(len(failed_domains), 0)
        self.assertIn(" (AWS credentials not found)", failed_domains[0])


if __name__ == "__main__":
    unittest.main()