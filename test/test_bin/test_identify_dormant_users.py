import unittest
from datetime import datetime, timedelta
from unittest.mock import mock_open, patch

from botocore.exceptions import ClientError, NoCredentialsError

from bin.identify_dormant_github_users import (
    calculate_date_by_integer, download_github_dormant_users_csv_from_s3,
    get_usernames_from_csv_ignoring_bots)


class TestDormantGitHubUsers(unittest.TestCase):

    def setUp(self):
        self.allowed_bot_users = ["bot1", "bot2"]

    def test_calculate_date_by_integer_valid_days(self):
        result = calculate_date_by_integer(7)
        expected_date = datetime.now() - timedelta(days=7)
        expected_date = expected_date.replace(
            hour=0, minute=0, second=0, microsecond=0)
        self.assertEqual(result, expected_date)

    def test_calculate_date_by_integer_zero_days(self):
        result = calculate_date_by_integer(0)
        expected_date = datetime.now()
        expected_date = expected_date.replace(
            hour=0, minute=0, second=0, microsecond=0)
        self.assertEqual(result, expected_date)

    def test_calculate_date_by_integer_negative_days(self):
        result = calculate_date_by_integer(-7)
        expected_date = datetime.now() + timedelta(days=7)
        expected_date = expected_date.replace(
            hour=0, minute=0, second=0, microsecond=0)
        self.assertEqual(result, expected_date)

    def test_get_usernames_from_csv_ignoring_bots_empty_csv(self):
        mock_file_content = ""
        with patch("builtins.open", mock_open(read_data=mock_file_content)):
            result = get_usernames_from_csv_ignoring_bots(
                self.allowed_bot_users)
        self.assertEqual(result, [])

    def test_get_usernames_from_csv_ignoring_bots_only_bots(self):
        mock_file_content = "ci-hmcts\ncloud-platform-dummy-user\n"
        with patch("builtins.open", mock_open(read_data=mock_file_content)):
            result = get_usernames_from_csv_ignoring_bots(
                self.allowed_bot_users)
        self.assertEqual(result, [])

    @patch('boto3.client')
    def test_download_github_dormant_users_csv_from_s3_no_credentials(self, mock_boto3_client):
        # Mock boto3 client to raise NoCredentialsError
        mock_boto3_client.side_effect = NoCredentialsError
        with self.assertRaises(NoCredentialsError):
            download_github_dormant_users_csv_from_s3()

    @patch('boto3.client')
    def test_download_github_dormant_users_csv_from_s3_file_not_found(self, mock_boto3_client):
        # Mock boto3 client to raise ClientError for a not found file
        error_response = {'Error': {'Code': '404', 'Message': 'Not Found'}}
        mock_boto3_client.side_effect = ClientError(
            error_response, 'get_object')
        with self.assertRaises(ClientError):
            download_github_dormant_users_csv_from_s3()

    @patch('os.environ.get')
    def test_dormant_users_according_to_github_all_active(self, mock_env_get):
        # Fill in test implementation
        pass

    @patch('os.environ.get')
    def test_dormant_users_according_to_github_all_dormant(self, mock_env_get):
        # Fill in test implementation
        pass

    @patch('os.environ.get')
    def test_dormant_users_according_to_github_missing_token(self, mock_env_get):
        # Mock `os.environ.get` to return `None` for `GH_ADMIN_TOKEN`
        mock_env_get.side_effect = lambda k: None if k == 'GH_ADMIN_TOKEN' else 'dummy_value'
        # Fill in test implementation

    def test_dormant_users_not_in_auth0_audit_log_all_present(self):
        # Fill in test implementation
        pass

    def test_dormant_users_not_in_auth0_audit_log_all_absent(self):
        # Fill in test implementation
        pass

    @patch('os.environ.get')
    def test_setup_services_success(self, mock_env_get):
        # Fill in test implementation
        pass

    @patch('os.environ.get')
    def test_setup_services_missing_gh_admin_token(self, mock_env_get):
        # Mock `os.environ.get` to return `None` for `GH_ADMIN_TOKEN`
        mock_env_get.side_effect = lambda k: None if k == 'GH_ADMIN_TOKEN' else 'dummy_value'
        # Fill in test implementation
        pass


if __name__ == '__main__':
    unittest.main()
