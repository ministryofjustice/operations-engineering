import unittest
from unittest.mock import patch, MagicMock
from botocore.exceptions import NoCredentialsError
from bin.check_mta_sts import main, check_mta_sts_domains, is_well_known_mta_sts_enforce

class TestMTASTS(unittest.TestCase):
    def setUp(self):
        self.s3_service = MagicMock()

    @patch('bin.check_mta_sts.is_well_known_mta_sts_enforce')
    def test_successful_retrieval_with_enforce(self, mock_is_enforce):
        mock_is_enforce.side_effect = lambda s3_client, domain: True
        failed_domains = check_mta_sts_domains(self.s3_service)
        self.assertEqual(len(failed_domains), 0)

    @patch('bin.check_mta_sts.is_well_known_mta_sts_enforce')
    def test_successful_retrieval_without_enforce(self, mock_is_enforce):
        mock_is_enforce.side_effect = lambda s3_client, domain: domain != 'example.com'
        failed_domains = check_mta_sts_domains(self.s3_service)
        self.assertIn("example.com", failed_domains)

    @patch('bin.check_mta_sts.is_well_known_mta_sts_enforce')
    def test_no_credentials(self, mock_is_enforce):
        mock_is_enforce.side_effect = NoCredentialsError()
        failed_domains = check_mta_sts_domains(self.s3_service)
        self.assertGreater(len(failed_domains), 0)

    @patch('bin.check_mta_sts.S3Service')
    @patch('bin.check_mta_sts.is_well_known_mta_sts_enforce')
    def test_main_function_with_enforce(self, mock_is_enforce, mock_s3_service):
        mock_is_enforce.side_effect = lambda s3_client, domain: True
        mock_s3_service.return_value = self.s3_service
        failed_domains = main()
        self.assertEqual(len(failed_domains), 0)

    @patch('bin.check_mta_sts.S3Service')
    @patch('bin.check_mta_sts.is_well_known_mta_sts_enforce')
    def test_main_function_without_enforce(self, mock_is_enforce, mock_s3_service):
        mock_is_enforce.side_effect = lambda s3_client, domain: domain != 'example.com'
        mock_s3_service.return_value = self.s3_service
        failed_domains = main()
        self.assertIn("example.com", failed_domains)

    @patch('bin.check_mta_sts.S3Service')
    @patch('bin.check_mta_sts.is_well_known_mta_sts_enforce')
    def test_main_function_no_credentials(self, mock_is_enforce, mock_s3_service):
        mock_is_enforce.side_effect = NoCredentialsError()
        mock_s3_service.return_value = self.s3_service
        failed_domains = main()
        self.assertGreater(len(failed_domains), 0)

    def test_main_function_direct_call_with_enforce(self):
        # Mock is_well_known_mta_sts_enforce directly for this test
        with patch('bin.check_mta_sts.is_well_known_mta_sts_enforce') as mock_is_enforce:
            mock_is_enforce.side_effect = lambda s3_client, domain: True
            self.s3_service.get_object = MagicMock(return_value={'Body': {'read': MagicMock(return_value=b'mode: enforce')}})
            failed_domains = main()
            self.assertEqual(len(failed_domains), 0)

    def test_main_function_direct_call_without_enforce(self):
        # Mock is_well_known_mta_sts_enforce directly for this test
        with patch('bin.check_mta_sts.is_well_known_mta_sts_enforce') as mock_is_enforce:
            mock_is_enforce.side_effect = lambda s3_client, domain: domain != 'example.com'
            self.s3_service.get_object = MagicMock(return_value={'Body': {'read': MagicMock(return_value=b'mode: none')}})
            failed_domains = main()
            self.assertIn("example.com", failed_domains)

    def test_main_function_direct_call_no_credentials(self):
        # Mock is_well_known_mta_sts_enforce directly for this test
        with patch('bin.check_mta_sts.is_well_known_mta_sts_enforce') as mock_is_enforce:
            mock_is_enforce.side_effect = NoCredentialsError()
            failed_domains = main()
            self.assertGreater(len(failed_domains), 0)

if __name__ == "__main__":
    unittest.main()
