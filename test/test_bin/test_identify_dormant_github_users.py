import unittest
from unittest.mock import MagicMock, patch

from bin.identify_dormant_github_users import (
    ALLOWED_BOT_USERS, DormantUser, filter_out_active_auth0_users,
    get_active_users_from_auth0_log_group, message_to_slack_channel)

from bin.identify_dormant_github_users_v2 import get_inactive_users_from_data_lake_ignoring_bots_and_collaborators

from services.cloudtrail_service import CloudtrailService

class TestDormantGitHubUsers(unittest.TestCase):

    def setUp(self):
        self.allowed_bot_users = ALLOWED_BOT_USERS

    @patch('services.cloudwatch_service.CloudWatchService.get_all_auth0_users_that_appear_in_tenants')
    def test_get_active_users_from_auth0_log_group(self, mock_get_users):
        mock_get_users.return_value = [
            'user1@example.com', 'user2@example.com']

        result = get_active_users_from_auth0_log_group()

        self.assertEqual(result, ['user1@example.com', 'user2@example.com'])

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

    def test_message_to_slack_channel(self):
        dormant_users = [
            DormantUser(name='user1', email='user1@example.com'),
            DormantUser(name='user2', email='user2@example.com')
        ]

        result = message_to_slack_channel(dormant_users)

        expected_message = (
            "Hello 🤖, \n\n"
            "Here is a list of dormant GitHub users that have not been seen in Auth0 logs:\n\n"
            "user1 | user1@example.com\n"
            "user2 | user2@example.com\n"
        )

        self.assertEqual(result, expected_message)

    @patch.object(CloudtrailService, "get_active_users_for_dormant_users_process")
    def test_get_inactive_users_from_data_lake_ignoring_bots_and_collaborators(self, mock_get_active_users_for_dormant_users_process):
        mock_get_active_users_for_dormant_users_process.return_value = ["member1"]
        mock_github_service = MagicMock()
        mock_github_service.get_all_enterprise_members = MagicMock(return_value=["member1", "member2", "bot1", "bot2"])

        assert get_inactive_users_from_data_lake_ignoring_bots_and_collaborators(mock_github_service, self.allowed_bot_users) == ["member2"]

if __name__ == "__main__":
    unittest.main()
