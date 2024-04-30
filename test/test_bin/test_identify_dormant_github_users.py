import unittest
from unittest.mock import mock_open, patch

from botocore.exceptions import ClientError, NoCredentialsError

from bin.identify_dormant_github_users import (
    DormantUserEnvironment, download_github_dormant_users_csv_from_s3,
    get_usernames_from_csv_ignoring_bots_and_collaborators)


class TestDormantUserEnvironment(unittest.TestCase):
    @patch.dict('os.environ', {
        'GH_ADMIN_TOKEN': 'test_github_token',
        'AUTH0_CLIENT_SECRET': 'test_auth0_secret',
        'AUTH0_CLIENT_ID': 'test_auth0_id',
        'ADMIN_SLACK_TOKEN': 'test_slack_token'
    })
    def test_environment_variables_set(self):
        env = DormantUserEnvironment()
        self.assertEqual(env.github_token, 'test_github_token')
        self.assertEqual(env.auth0_secret_token, 'test_auth0_secret')
        self.assertEqual(env.auth0_id_token, 'test_auth0_id')
        self.assertEqual(env.slack_token, 'test_slack_token')

    @patch.dict('os.environ', {
        'GH_ADMIN_TOKEN': '',
        'AUTH0_CLIENT_SECRET': 'test_auth0_secret',
        'AUTH0_CLIENT_ID': 'test_auth0_id',
        'ADMIN_SLACK_TOKEN': 'test_slack_token'
    })
    def test_missing_github_token(self):
        with self.assertRaises(ValueError) as context:
            DormantUserEnvironment()
        self.assertTrue("GH_ADMIN_TOKEN is not set" in str(context.exception))

    @patch.dict('os.environ', {
        'GH_ADMIN_TOKEN': 'test_github_token',
        'AUTH0_CLIENT_SECRET': '',
        'AUTH0_CLIENT_ID': 'test_auth0_id',
        'ADMIN_SLACK_TOKEN': 'test_slack_token'
    })
    def test_missing_auth0_secret(self):
        with self.assertRaises(ValueError) as context:
            DormantUserEnvironment()
        self.assertTrue(
            "AUTH0_CLIENT_SECRET or AUTH0_CLIENT_ID is not set" in str(context.exception))

    @patch.dict('os.environ', {
        'GH_ADMIN_TOKEN': 'test_github_token',
        'AUTH0_CLIENT_SECRET': 'test_auth0_secret',
        'AUTH0_CLIENT_ID': '',
        'ADMIN_SLACK_TOKEN': 'test_slack_token'
    })
    def test_missing_auth0_id(self):
        with self.assertRaises(ValueError) as context:
            DormantUserEnvironment()
        self.assertTrue(
            "AUTH0_CLIENT_SECRET or AUTH0_CLIENT_ID is not set" in str(context.exception))


class TestDormantGitHubUsers(unittest.TestCase):

    def setUp(self):
        self.allowed_bot_users = ["bot1", "bot2"]

    def test_get_usernames_from_csv_ignoring_bots_empty_csv(self):
        mock_file_content = ""
        with patch("builtins.open", mock_open(read_data=mock_file_content)):
            result = get_usernames_from_csv_ignoring_bots_and_collaborators(
                self.allowed_bot_users)
        self.assertEqual(result, [])

    def test_get_usernames_from_csv_ignoring_bots_only_bots(self):
        mock_file_content = "created_at,id,login,role,last_logged_ip,2fa_enabled?,outside_collaborator\n2011-05-04 10:06:20 +0100,767430,bot2,user,165.225.16.122,true,false\n2012-06-19 10:02:40 +0100,1866734,bot1,user,31.121.104.4,true,false"
        bot_list = ['bot1', 'bot2']
        with patch("builtins.open", mock_open(read_data=mock_file_content)):
            result = get_usernames_from_csv_ignoring_bots_and_collaborators(
                bot_list=bot_list)
        self.assertEqual(result, [])

    def test_get_usernames_from_csv_ignoring_bots_and_collaborators(self):
        mock_file_content = "created_at,id,login,role,last_logged_ip,2fa_enabled?,outside_collaborator\n2011-05-04 10:06:20 +0100,767430,joebloggs,user,165.225.16.122,true,false\n2012-06-19 10:02:40 +0100,1866734,jamesoutsidecollaborator,user,31.121.104.4,true,true"
        bot_list = ['bot1', 'bot2']
        with patch("builtins.open", mock_open(read_data=mock_file_content)):
            usernames = get_usernames_from_csv_ignoring_bots_and_collaborators(
                bot_list)
        self.assertEqual(usernames, ['joebloggs'])

    @ patch('boto3.client')
    def test_download_github_dormant_users_csv_from_s3_no_credentials(self, mock_boto3_client):
        # Mock boto3 client to raise NoCredentialsError
        mock_boto3_client.side_effect = NoCredentialsError
        with self.assertRaises(NoCredentialsError):
            download_github_dormant_users_csv_from_s3()

    @ patch('boto3.client')
    def test_download_github_dormant_users_csv_from_s3_file_not_found(self, mock_boto3_client):
        # Mock boto3 client to raise ClientError for a not found file
        error_response = {'Error': {'Code': '404', 'Message': 'Not Found'}}
        mock_boto3_client.side_effect = ClientError(
            error_response, 'get_object')
        with self.assertRaises(ClientError):
            download_github_dormant_users_csv_from_s3()


if __name__ == '__main__':
    unittest.main()
