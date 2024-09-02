import unittest
from unittest.mock import patch

from bin.identify_dormant_github_users import (
    ALLOWED_BOT_USERS, DormantUser, filter_out_active_auth0_users,
    get_active_users_from_auth0_log_group, message_to_slack_channel)


class TestDormantGitHubUsers(unittest.TestCase):

    def setUp(self):
        self.allowed_bot_users = ALLOWED_BOT_USERS

    @patch('services.cloudwatch_service.CloudWatchService')
    def test_get_active_users_from_auth0_log_group(self, MockCloudWatchService):
        mock_service = MockCloudWatchService.return_value
        mock_service.get_all_auth0_users_that_appear_in_tenants.return_value = [
            'user1@example.com', 'user2@example.com']

        result = get_active_users_from_auth0_log_group()

        self.assertEqual(result, ['user1@example.com', 'user2@example.com'])

    def test_filter_out_active_auth0_users(self):
        dormant_users_according_to_github = [
            DormantUser(name='user1', email='user1@example.com'),
            DormantUser(name='user2', email='user2@example.com'),
            DormantUser(name='user3', email='user3@example.com')
        ]
        active_email_addresses = ['user1@example.com', 'user3@example.com']

        result = filter_out_active_auth0_users(
            dormant_users_according_to_github)

        expected_result = [DormantUser(
            name='user2', email='user2@example.com')]
        self.assertEqual(result, expected_result)

    def test_message_to_slack_channel(self):
        dormant_users = [
            DormantUser(name='user1', email='user1@example.com'),
            DormantUser(name='user2', email='user2@example.com')
        ]

        result = message_to_slack_channel(dormant_users)

        expected_message = (
            "Hello 🤖, \n\n"
            "The identify dormant GitHub users script has identified 2 dormant users. \n-----\n"
            "GitHub username: user1 | Email: user1@example.com\n"
            "GitHub username: user2 | Email: user2@example.com\n"
        )
        self.assertEqual(result, expected_message)


if __name__ == "__main__":
    unittest.main()
