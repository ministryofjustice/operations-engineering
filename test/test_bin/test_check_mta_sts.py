import unittest
from unittest.mock import patch, MagicMock
from botocore.exceptions import NoCredentialsError

# Import the module containing the original code
from check_mta_sts import s3, domains, SUFFIX, failed_domains

class TestMTASTSChecker(unittest.TestCase):

    def setUp(self):
        # Clear the failed_domains list before each test
        failed_domains.clear()

    @patch('check_mta_sts.s3.get_object')
    def test_successful_retrieval_with_enforce(self, mock_get_object):
        """Test successful retrieval of MTA-STS configuration with 'mode: enforce'."""
        mock_response = MagicMock()
        mock_response['Body'].read.return_value = b"version: STSv1\nmode: enforce\n"
        mock_get_object.return_value = mock_response

        # Run the original code logic
        for domain in domains:
            bucket_name = f"880656497252.{domain}"
            try:
                response = s3.get_object(Bucket=bucket_name, Key=SUFFIX)
                sts_content = response['Body'].read().decode('utf-8')
                has_enforce = any(line.startswith("mode: enforce") for line in sts_content.split('\n'))
                if not has_enforce:
                    failed_domains.append(f"{domain} (No 'mode: enforce')")
            except NoCredentialsError:
                failed_domains.append(f"{domain} (AWS credentials not found)")
            except Exception as e:
                failed_domains.append(f"{domain} (Exception: {e})")

        self.assertEqual(len(failed_domains), 0)

    @patch('check_mta_sts.s3.get_object')
    def test_successful_retrieval_without_enforce(self, mock_get_object):
        """Test successful retrieval of MTA-STS configuration without 'mode: enforce'."""
        mock_response = MagicMock()
        mock_response['Body'].read.return_value = b"version: STSv1\nmode: testing\n"
        mock_get_object.return_value = mock_response

        # Run the original code logic
        for domain in domains:
            bucket_name = f"880656497252.{domain}"
            try:
                response = s3.get_object(Bucket=bucket_name, Key=SUFFIX)
                sts_content = response['Body'].read().decode('utf-8')
                has_enforce = any(line.startswith("mode: enforce") for line in sts_content.split('\n'))
                if not has_enforce:
                    failed_domains.append(f"{domain} (No 'mode: enforce')")
            except NoCredentialsError:
                failed_domains.append(f"{domain} (AWS credentials not found)")
            except Exception as e:
                failed_domains.append(f"{domain} (Exception: {e})")

        self.assertGreater(len(failed_domains), 0)
        self.assertIn(" (No 'mode: enforce')", failed_domains[0])

    @patch('check_mta_sts.s3.get_object', side_effect=NoCredentialsError)
    def test_no_credentials(self, mock_get_object):
        """Test handling of missing AWS credentials."""
        # Run the original code logic
        for domain in domains:
            bucket_name = f"880656497252.{domain}"
            try:
                response = s3.get_object(Bucket=bucket_name, Key=SUFFIX)
                sts_content = response['Body'].read().decode('utf-8')
                has_enforce = any(line.startswith("mode: enforce") for line in sts_content.split('\n'))
                if not has_enforce:
                    failed_domains.append(f"{domain} (No 'mode: enforce')")
            except NoCredentialsError:
                failed_domains.append(f"{domain} (AWS credentials not found)")
            except Exception as e:
                failed_domains.append(f"{domain} (Exception: {e})")

        self.assertGreater(len(failed_domains), 0)
        self.assertIn(" (AWS credentials not found)", failed_domains[0])
if __name__ == '__main__':
    unittest.main()        
