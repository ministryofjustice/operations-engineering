# pylint: disable=W0221, C0411

import unittest
from unittest.mock import MagicMock, patch

from services.slack_service import SlackService

@patch("slack_sdk.WebClient.__new__")
class TestSlackServiceInit(unittest.TestCase):

    def test_sets_up_class(self, mock_slack_client: MagicMock):
        mock_slack_client.return_value = "test_mock"
        slack_service = SlackService("")
        self.assertEqual("test_mock",
                         slack_service.slack_client)


class TestSendMessageToPlainTextChannelName(unittest.TestCase):

    @patch("slack_sdk.WebClient.__new__")
    def setUp(self, mock_web_client):
        self.channel_name = 'test_channel'
        self.message = 'test message'
        self.channel_id = 'test_channel_id'
        self.response_metadata = {'next_cursor': ''}
        self.channel = {'name': self.channel_name, 'id': self.channel_id}
        self.response = {'ok': True}
        self.slack_client = MagicMock()
        self.mock_web_client = mock_web_client
        self.mock_web_client.return_value = self.slack_client
        self.slack_service = SlackService("")
        self.slack_client.conversations_list.return_value = {
            'channels': [self.channel], 'response_metadata': self.response_metadata}
        self.slack_service.slack_client = self.slack_client


@patch("slack_sdk.WebClient.__new__")
class SendUnknownUserAlertToOperationsEngineering(unittest.TestCase):

    def test_downstream_services_called(self, mock_slack_client: MagicMock):
        users = ["some-user1", "some-user2", "some-user3"]
        SlackService(
            "").send_unknown_user_alert_to_operations_engineering(users)
        mock_slack_client.return_value.chat_postMessage.assert_called_with(
            channel="C033QBE511V",
            mrkdown=True,
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": '*Dormant Users Automation*\n\nRemove these users from the Dormant Users allow list:\n[\'some-user1\', \'some-user2\', \'some-user3\']'
                    }
                }
            ]
        )


@patch("slack_sdk.WebClient.__new__")
class SendRemoveUsersFromGithubAlertToOperationsEngineering(unittest.TestCase):

    def test_downstream_services_called(self, mock_slack_client: MagicMock):
        SlackService("").send_remove_users_from_github_alert_to_operations_engineering(
            3, "some-org")
        mock_slack_client.return_value.chat_postMessage.assert_called_with(
            channel="C033QBE511V",
            mrkdown=True,
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": '*Dormant Users Automation*\n\nRemoved 3 users from the some-org GitHub Organisation.\n\nSee the GH Action for more info: https://github.com/ministryofjustice/operations-engineering'
                    }
                }
            ]
        )


@patch("slack_sdk.WebClient.__new__")
class SendUndeliveredEmailAlertToOperationsEngineering(unittest.TestCase):

    def test_downstream_services_called(self, mock_slack_client: MagicMock):
        email_address = ["some-user1@domain.com",
                         "some-user2@domain.com", "some-user3@domain.com"]
        SlackService("").send_undelivered_email_alert_to_operations_engineering(
            email_address, "some-org")
        mock_slack_client.return_value.chat_postMessage.assert_called_with(
            channel="C033QBE511V",
            mrkdown=True,
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": '*Dormant Users Automation*\n\nUndelivered emails for some-org GitHub Organisation:\n[\'some-user1@domain.com\', \'some-user2@domain.com\', \'some-user3@domain.com\']\n\nRemove these users manually.'
                    }
                }
            ]
        )


class TestSlackService(unittest.TestCase):

    @patch("slack_sdk.WebClient.__new__")
    def setUp(self, mock_slack_client):
        self.message = "some-message"
        self.blocks = [
            {
                "type": "section",
                "text": {
                        "type": "mrkdwn",
                        "text": self.message
                }
            }
        ]
        self.mock_slack_client = mock_slack_client
        self.slack_service = SlackService("")

    def test_create_block_with_message(self):
        self.assertEqual(
            self.blocks, self.slack_service._create_block_with_message(self.message))

    def test_send_alert_to_operations_engineering(self):
        self.slack_service._send_alert_to_operations_engineering(self.blocks)
        self.mock_slack_client.return_value.chat_postMessage.assert_called_with(
            channel="C033QBE511V",
            mrkdown=True,
            blocks=self.blocks
        )

    def test_send_dormant_user_list(self):
        user_list = "Test user list"
        expected_message = (
            "*Dormant User Report*\n\n"
            "Here is a list of dormant GitHub users that have not been seen in Auth0 logs for 13 days:\n"
            f"{user_list}"
        )
        blocks = self.slack_service._create_block_with_message(expected_message)
        self.slack_service.send_dormant_user_list(user_list, str(13))
        self.mock_slack_client.return_value.chat_postMessage.assert_called_once_with(
            channel="C033QBE511V", mrkdown=True, blocks=blocks
        )

    def test_send_unknown_user_alert_to_operations_engineering(self):
        users = ["user1", "user2"]
        expected_message = (
            "*Dormant Users Automation*\n\n"
            "Remove these users from the Dormant Users allow list:\n"
            f"{users}"
        )
        blocks = self.slack_service._create_block_with_message(expected_message)
        self.slack_service.send_unknown_user_alert_to_operations_engineering(users)
        self.mock_slack_client.return_value.chat_postMessage.assert_called_once_with(
            channel="C033QBE511V", mrkdown=True, blocks=blocks
        )

    def test_send_remove_users_from_github_alert(self):
        number_of_users = 3
        organisation_name = "Test Org"
        expected_message = (
            "*Dormant Users Automation*\n\n"
            f"Removed {number_of_users} users from the {organisation_name} GitHub Organisation.\n\n"
            f"See the GH Action for more info: https://github.com/ministryofjustice/operations-engineering"
        )
        blocks = self.slack_service._create_block_with_message(expected_message)
        self.slack_service.send_remove_users_from_github_alert_to_operations_engineering(number_of_users, organisation_name)
        self.mock_slack_client.return_value.chat_postMessage.assert_called_once_with(
            channel="C033QBE511V", mrkdown=True, blocks=blocks
        )

    def test_send_unknown_users_slack_message(self):
        self.slack_service.send_unknown_users_slack_message(
            ["some-user1", "some-user2", "some-user3"])
        self.mock_slack_client.return_value.chat_postMessage.assert_called_with(
            channel="C033QBE511V",
            mrkdown=True,
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": '*Dormant Users Automation*\nRemove these users from the Dormant Users allow list:\n[\'some-user1\', \'some-user2\', \'some-user3\']'
                    }
                }
            ]
        )

    def test_send_remove_users_slack_message(self):
        self.slack_service.send_remove_users_slack_message(
            3, "some-org")
        self.mock_slack_client.return_value.chat_postMessage.assert_called_with(
            channel="C033QBE511V",
            mrkdown=True,
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": '*Dormant Users Automation*\nRemoved 3 users from the some-org GitHub Organisation.\nSee the GH Action for more info: https://github.com/ministryofjustice/operations-engineering'
                    }
                }
            ]
        )

    def test_send_undelivered_emails_slack_message(self):
        email_address = ["some-user1@domain.com",
                         "some-user2@domain.com",
                         "some-user3@domain.com"
                         ]
        self.slack_service.send_undelivered_emails_slack_message(
            email_address, "some-org")
        self.mock_slack_client.return_value.chat_postMessage.assert_called_with(
            channel="C033QBE511V",
            mrkdown=True,
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": '*Dormant Users Automation*\nUndelivered emails for some-org GitHub Organisation:\n[\'some-user1@domain.com\', \'some-user2@domain.com\', \'some-user3@domain.com\']\nRemove these users manually'
                    }
                }
            ]
        )


if __name__ == "__main__":
    unittest.main()
