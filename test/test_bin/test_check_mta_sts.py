# pylint: disable=wrong-import-order
import unittest
from unittest.mock import patch, MagicMock
from botocore.exceptions import NoCredentialsError
from bin.check_mta_sts import SUFFIX, domains, S3Service, main, is_well_known_mta_sts_enforce

class TestMTASTS(unittest.TestCase):
    def setUp(self):
        """Set up mock S3 client and initialize test data."""
        self.s3_service = S3Service("880656497252", "ministryofjustice")
        self.failed_domains = []

    def run_test_logic(self, mock_is_enforce, expected_mode):
        """Run the original code logic and check for expected errors."""
        for domain in domains:
            try:
                if not mock_is_enforce(domain, expected_mode):
                    self.failed_domains.append(f"{domain} (No '{expected_mode}')")
            except NoCredentialsError:
                self.failed_domains.append(f"{domain} (AWS credentials not found)")
            except ValueError as e:
                self.failed_domains.append(f"{domain} (Exception: {e})")

    @patch('bin.check_mta_sts.is_well_known_mta_sts_enforce')
    def test_successful_retrieval_with_enforce(self, mock_is_enforce):
        """Test successful retrieval of MTA-STS configuration with 'mode: enforce'."""
        mock_is_enforce.side_effect = lambda domain, mode: True
        self.run_test_logic(mock_is_enforce, "enforce")
        self.assertEqual(len(self.failed_domains), 0, f"Failed domains: {self.failed_domains}")

    @patch('bin.check_mta_sts.is_well_known_mta_sts_enforce')
    def test_successful_retrieval_without_enforce(self, mock_is_enforce):
        """Test successful retrieval of MTA-STS configuration without 'mode: enforce'."""
        mock_is_enforce.side_effect = lambda domain, mode: domain != 'example.com'
        self.run_test_logic(mock_is_enforce, "testing")
        self.assertGreater(len(self.failed_domains), 0, f"Failed domains: {self.failed_domains}")
        self.assertIn("example.com (No 'testing')", self.failed_domains)

    @patch('bin.check_mta_sts.is_well_known_mta_sts_enforce')
    def test_no_credentials(self, mock_is_enforce):
        """Test handling of missing AWS credentials."""
        mock_is_enforce.side_effect = lambda domain, mode: True
        self.run_test_logic(mock_is_enforce, "enforce")
        self.assertGreater(len(self.failed_domains), 0, f"Failed domains: {self.failed_domains}")
        self.assertIn("example.com (AWS credentials not found)", self.failed_domains)

if __name__ == "__main__":
    unittest.main()
