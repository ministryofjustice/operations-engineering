import unittest
from unittest.mock import mock_open, patch

from botocore.exceptions import ClientError, NoCredentialsError

from bin.identify_dormant_github_users import (
    ALLOWED_BOT_USERS, DormantUserProcessEnvironment,
    download_github_dormant_users_csv_from_s3,
    get_dormant_users_from_github_csv,
    get_usernames_from_csv_ignoring_bots_and_collaborators)


class TestDormantUserEnvironment(unittest.TestCase):
    @ patch.dict('os.environ', {
        'GH_ADMIN_TOKEN': 'test_github_token',
        'ADMIN_SLACK_TOKEN': 'test_slack_token'
    })
    def test_environment_variables_set(self):
        env = DormantUserProcessEnvironment()
        self.assertEqual(env.github_token, 'test_github_token')
        self.assertEqual(env.slack_token, 'test_slack_token')

    @ patch.dict('os.environ', {
        'GH_ADMIN_TOKEN': '',
        'ADMIN_SLACK_TOKEN': 'test_slack_token'
    })
    def test_missing_github_token(self):
        with self.assertRaises(ValueError) as context:
            DormantUserProcessEnvironment()
        self.assertTrue("GH_ADMIN_TOKEN is not set" in str(context.exception))

    @ patch.dict('os.environ', {
        'GH_ADMIN_TOKEN': 'test_github_token',
        'ADMIN_SLACK_TOKEN': ''
    })
    def test_missing_slack_token(self):
        with self.assertRaises(ValueError) as context:
            DormantUserProcessEnvironment()
        self.assertTrue(
            "ADMIN_SLACK_TOKEN is not set" in str(context.exception))


class TestDormantGitHubUsers(unittest.TestCase):

    def setUp(self):
        self.allowed_bot_users = ["bot1", "bot2"]

    @patch('bin.identify_dormant_github_users.download_github_dormant_users_csv_from_s3')
    @patch('bin.identify_dormant_github_users.get_usernames_from_csv_ignoring_bots_and_collaborators')
    @patch('services.dormant_github_user_service.DormantGitHubUser')
    @patch('services.github_service.GithubService')
    def test_get_dormant_users_from_github_csv(self, mock_github_service, mock_dormant_github_user, mock_get_usernames, mock_download_csv):
        mock_get_usernames.return_value = ['user1', 'user2', 'user3']

        mock_dormant_github_user.side_effect = lambda github_service, user: MagicMock(
            __str__=lambda: f'DormantGitHubUser({user})')
        github_service = mock_github_service

        result = get_dormant_users_from_github_csv(github_service)

        self.assertEqual(len(result), 3)
        mock_download_csv.assert_called_once()
        mock_get_usernames.assert_called_once_with(ALLOWED_BOT_USERS)

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
