import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, mock_open, patch

from botocore.exceptions import ClientError, NoCredentialsError

from bin.identify_dormant_github_users import (
    calculate_date_by_integer, dormant_users_according_to_github,
    dormant_users_not_in_auth0_audit_log,
    download_github_dormant_users_csv_from_s3,
    get_usernames_from_csv_ignoring_bots_and_collaborators, setup_services)
from services.auth0_service import Auth0Service
from services.github_service import GithubService


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
            result = get_usernames_from_csv_ignoring_bots_and_collaborators(
                self.allowed_bot_users)
        self.assertEqual(result, [])

    @patch("builtins.open", new_callable=mock_open, read_data="created_at,id,login,role,last_logged_ip,2fa_enabled?,outside_collaborator\n2011-05-04 10:06:20 +0100,767430,bot2,user,165.225.16.122,true,false\n2012-06-19 10:02:40 +0100,1866734,bot1,user,31.121.104.4,true,false")
    def test_get_usernames_from_csv_ignoring_bots_only_bots(self, mock_file_content):
        bot_list = ['bot1', 'bot2']
        result = get_usernames_from_csv_ignoring_bots_and_collaborators(
            bot_list=bot_list)
        self.assertEqual(result, [])

    @patch("builtins.open", new_callable=mock_open, read_data="created_at,id,login,role,last_logged_ip,2fa_enabled?,outside_collaborator\n2011-05-04 10:06:20 +0100,767430,joebloggs,user,165.225.16.122,true,false\n2012-06-19 10:02:40 +0100,1866734,jamesoutsidecollaborator,user,31.121.104.4,true,true")
    def test_get_usernames_from_csv_ignoring_bots_and_collaborators(self, mock_file):
        bot_list = ['bot1', 'bot2']
        usernames = get_usernames_from_csv_ignoring_bots_and_collaborators(
            bot_list)
        self.assertEqual(usernames, ['joebloggs'])

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

    @patch.object(GithubService, "__new__")
    @patch('bin.identify_dormant_github_users.get_dormant_users_from_github_csv')
    def test_dormant_users_according_to_github_all_active(self, mock_get_dormant_users_from_github_csv, mock_github_service):
        # Mock `get_dormant_users_from_github_csv` to return a list of users
        mock_get_dormant_users_from_github_csv.return_value = [
            'user1', 'user2']
        # Mock `github_service` to return an empty set
        mock_github_service.check_dormant_users_audit_activity_since_date.return_value = set()
        result = dormant_users_according_to_github(
            mock_github_service, datetime.now() - timedelta(days=30))
        self.assertEqual(result, set())

    @patch.object(GithubService, "__new__")
    @patch('bin.identify_dormant_github_users.get_dormant_users_from_github_csv')
    def test_dormant_users_according_to_github_all_dormant(self, mock_get_dormant_users_from_github_csv, mock_github_service):
        # Mock `get_dormant_users_from_github_csv` to return a list of users
        mock_get_dormant_users_from_github_csv.return_value = [
            'user1', 'user2']
        # Mock `github_service` to return a set of users
        mock_github_service.check_dormant_users_audit_activity_since_date.return_value = {
            'user1', 'user2'}
        result = dormant_users_according_to_github(
            mock_github_service, datetime.now() - timedelta(days=30))
        self.assertEqual(result, {'user1', 'user2'})

    def test_dormant_users_not_in_auth0_audit_log_all_present(self):
        # Mock `auth0_service` to return a set of users
        mock_auth0_service = MagicMock(spec=Auth0Service)
        mock_auth0_service.get_active_case_sensitive_usernames.return_value = {
            'user1', 'user2'}
        result = dormant_users_not_in_auth0_audit_log(
            mock_auth0_service, {'user1', 'user2'})
        self.assertEqual(result, set())

    def test_dormant_users_not_in_auth0_audit_log_all_absent(self):
        # Mock `auth0_service` to return an empty set
        mock_auth0_service = MagicMock(spec=Auth0Service)
        mock_auth0_service.get_active_case_sensitive_usernames.return_value = []
        result = dormant_users_not_in_auth0_audit_log(
            mock_auth0_service, {'user1', 'user2'})
        self.assertEqual(result, {'user1', 'user2'})

    @patch('os.environ.get')
    def test_setup_services_missing_gh_admin_token(self, mock_env_get):
        # Mock `os.environ.get` to return `None` for `GH_ADMIN_TOKEN`
        mock_env_get.side_effect = lambda k: None if k == 'GH_ADMIN_TOKEN' else 'dummy_value'
        with self.assertRaises(ValueError):
            setup_services()


if __name__ == '__main__':
    unittest.main()
