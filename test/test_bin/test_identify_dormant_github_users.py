import unittest
from unittest.mock import MagicMock, patch
from config.constants import MINISTRY_OF_JUSTICE, MOJ_ANALYTICAL_SERVICES

from bin.identify_dormant_github_users import (
    ALLOWED_BOT_USERS, DormantUser, filter_out_active_auth0_users,
    get_active_users_from_auth0_log_group)

from bin.identify_dormant_github_users_v2 import get_inactive_users_from_data_lake_ignoring_bots_and_collaborators, identify_dormant_github_users

from services.cloudtrail_service import CloudtrailService
from services.github_service import GithubService

class TestDormantGitHubUsers(unittest.TestCase):

    def setUp(self):
        self.allowed_bot_users = ALLOWED_BOT_USERS

    @patch('bin.identify_dormant_github_users.get_active_users_from_auth0_log_group')
    def test_filter_out_active_auth0_users(self, mock_get_active_users):
        mock_get_active_users.return_value = [
            'user1@example.com', 'user3@example.com']

        dormant_users_according_to_github = [
            DormantUser(name='user1', email='user1@example.com'),
            DormantUser(name='user2', email='user2@example.com'),
            DormantUser(name='user3', email='user3@example.com')
        ]

        result = filter_out_active_auth0_users(
            dormant_users_according_to_github)

        expected_result = [DormantUser(
            name='user2', email='user2@example.com')]

        self.assertIn(expected_result[0], result)

    @patch.object(CloudtrailService, "get_active_users_for_dormant_users_process")
    def test_get_inactive_users_from_data_lake_ignoring_bots_and_collaborators(self, mock_get_active_users_for_dormant_users_process):
        mock_get_active_users_for_dormant_users_process.return_value = ["member1"]
        mock_github_service = MagicMock()
        mock_github_service.get_all_enterprise_members = MagicMock(return_value=["member1", "member2", "analytical-platform-bot", "cloud-platform-dummy-user"])

        assert get_inactive_users_from_data_lake_ignoring_bots_and_collaborators(mock_github_service, self.allowed_bot_users) == ["member2"]

    @patch("gql.transport.aiohttp.AIOHTTPTransport.__new__", new=MagicMock)
    @patch("gql.Client.__new__", new=MagicMock)
    @patch("services.github_service.Github")
    @patch('bin.identify_dormant_github_users_v2.get_inactive_committers')
    @patch('bin.identify_dormant_github_users_v2.filter_out_active_auth0_users')
    @patch('bin.identify_dormant_github_users_v2.map_usernames_to_emails')
    @patch('bin.identify_dormant_github_users_v2.get_inactive_users_from_data_lake_ignoring_bots_and_collaborators')
    @patch('os.environ')
    def test_identify_dormant_github_users(self,
        mock_env,
        mock_get_inactive_users_from_data_lake_ignoring_bots_and_collaborators,
        mock_map_usernames_to_emails,
        mock_filter_out_active_auth0_users,
        mock_get_inactive_committers,
        _mock_github_client_core_api
    ):
        mock_env.get.side_effect = lambda k: 'mock_token' if k in ['GH_ADMIN_TOKEN'] else None
        mock_map_usernames_to_emails.return_value = [{"name": "user1", "email": "user1@gmail.com"}, {"name": "user2", "email": "user1@gmail.com"}, {"name": "user3", "email": "user1@gmail.com"}]
        mock_filter_out_active_auth0_users.return_value = ["user1", "user2"]

        identify_dormant_github_users()

        mock_get_inactive_users_from_data_lake_ignoring_bots_and_collaborators.assert_called_once()
        mock_map_usernames_to_emails.assert_called_once()
        mock_filter_out_active_auth0_users.assert_called_once_with([{"name": "user1", "email": "user1@gmail.com"}, {"name": "user2", "email": "user1@gmail.com"}, {"name": "user3", "email": "user1@gmail.com"}])
        mock_get_inactive_committers.assert_called_once()


if __name__ == "__main__":
    unittest.main()
