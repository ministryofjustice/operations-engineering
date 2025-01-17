import unittest
from unittest.mock import MagicMock, patch

from bin.identify_dormant_github_users_v2 import ALLOWED_BOT_USERS, get_inactive_users_from_data_lake_ignoring_bots_and_collaborators, identify_dormant_github_users

from services.cloudtrail_service import CloudtrailService

class TestDormantGitHubUsers(unittest.TestCase):

    def setUp(self):
        self.allowed_bot_users = ALLOWED_BOT_USERS

    @patch.object(CloudtrailService, "get_active_users_for_dormant_users_process")
    def test_get_inactive_users_from_data_lake_ignoring_bots_and_collaborators(self, mock_get_active_users_for_dormant_users_process):
        mock_get_active_users_for_dormant_users_process.return_value = ["member1"]
        mock_github_service = MagicMock()
        mock_github_service.get_all_enterprise_members = MagicMock(return_value=["member1", "member2", "analytical-platform-bot", "cloud-platform-dummy-user"])

        assert get_inactive_users_from_data_lake_ignoring_bots_and_collaborators(mock_github_service, self.allowed_bot_users, False) == ["member2"]

    @patch("gql.transport.aiohttp.AIOHTTPTransport.__new__", new=MagicMock)
    @patch("gql.Client.__new__", new=MagicMock)
    @patch("services.github_service.Github")
    @patch('bin.identify_dormant_github_users_v2.filter_out_inactive_committers')
    @patch('bin.identify_dormant_github_users_v2.filter_out_active_auth0_users')
    @patch('bin.identify_dormant_github_users_v2.map_usernames_to_emails')
    @patch('bin.identify_dormant_github_users_v2.get_inactive_users_from_data_lake_ignoring_bots_and_collaborators')
    @patch('os.environ')
    def test_identify_dormant_github_users(self, mock_env, _mock_get_inactive_users_from_data_lake_ignoring_bots_and_collaborators, mock_map_usernames_to_emails, mock_filter_out_active_auth0_users, mock_filter_out_inactive_committers, _mock_github_client_core_api):
        mock_env.get.side_effect = lambda k: 'mock_token' if k in ['GH_ADMIN_TOKEN', 'ADMIN_SLACK_TOKEN', 'USE_MP_INFRASTRUCTURE'] else None
        mock_map_usernames_to_emails.return_value = [{"name": "user1", "email": "user1@gmail.com"}, {"name": "user2", "email": "user1@gmail.com"}, {"name": "user3", "email": "user1@gmail.com"}]
        mock_filter_out_active_auth0_users.return_value = ["user1", "user2"]

        identify_dormant_github_users()

        mock_map_usernames_to_emails.assert_called_once()
        mock_filter_out_active_auth0_users.assert_called_once_with([{"name": "user1", "email": "user1@gmail.com"}, {"name": "user2", "email": "user1@gmail.com"}, {"name": "user3", "email": "user1@gmail.com"}])
        mock_filter_out_inactive_committers.assert_called_once()


if __name__ == "__main__":
    unittest.main()
