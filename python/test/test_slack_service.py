import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch

from python.services.sentry_service import UsageStats
from python.services.slack_service import SlackService

START_TIME = "2023-06-08T00:00:00Z"
END_TIME = "2023-06-09T00:00:00Z"
DATE_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


@patch("slack_sdk.WebClient.__new__")
class TestSlackServiceInit(unittest.TestCase):

    def test_sets_up_class(self, mock_slack_client: MagicMock):
        mock_slack_client.return_value = "test_mock"
        slack_service = SlackService("")
        self.assertEqual("test_mock",
                         slack_service.slack_client)


@patch("slack_sdk.WebClient.__new__")
class TestSendMessageToPlainTextChannelName(unittest.TestCase):

    def test_send_message_to_plaintext_channel_name(self, mock_web_client):
        channel_name = 'test_channel'
        message = 'test message'
        channel_id = 'test_channel_id'
        response_metadata = {'next_cursor': ''}
        channel = {'name': channel_name, 'id': channel_id}
        response = {'ok': True}
        slack_client = MagicMock()
        mock_web_client.return_value = slack_client
        slack_client.conversations_list.return_value = {'channels': [channel], 'response_metadata': response_metadata}
        slack_client.chat_postMessage.return_value = response

        service = SlackService("")
        service.slack_client = slack_client
        service.send_message_to_plaintext_channel_name(message, channel_name)

        slack_client.conversations_list.assert_called_once_with(limit=200, cursor='')
        slack_client.chat_postMessage.assert_called_once_with(channel=channel_id, text=message)

    def test_lookup_channel_id(self, mock_web_client):
        channel_name = 'test_channel'
        channel_id = 'test_channel_id'
        response_metadata = {'next_cursor': ''}
        channel = {'name': channel_name, 'id': channel_id}
        response = {'channels': [channel], 'response_metadata': response_metadata}
        slack_client = MagicMock()
        mock_web_client.return_value = slack_client
        slack_client.conversations_list.return_value = response

        service = SlackService("")
        service.slack_client = slack_client
        result = service._lookup_channel_id(channel_name)

        slack_client.conversations_list.assert_called_once_with(limit=200, cursor='')
        self.assertEqual(result, channel_id)

    def test_lookup_channel_id_not_found(self, mock_web_client):
        channel_name = 'test_channel'
        response_metadata = {'next_cursor': ''}
        response = {'channels': [], 'response_metadata': response_metadata}
        slack_client = MagicMock()
        mock_web_client.return_value = slack_client
        slack_client.conversations_list.return_value = response

        service = SlackService("")
        service.slack_client = slack_client
        result = service._lookup_channel_id(channel_name)

        slack_client.conversations_list.assert_called_once_with(limit=200, cursor='')
        self.assertIsNone(result)


@patch("slack_sdk.WebClient.__new__")
class TestSlackServiceSendErrorUsageAlertToOperationsEngineering(unittest.TestCase):

    def test_downstream_services_called(self, mock_slack_client: MagicMock):
        SlackService("").send_error_usage_alert_to_operations_engineering(
            0, UsageStats(1, 2, 3, start_time=datetime.strptime(START_TIME,
                                                                DATE_FORMAT),
                          end_time=datetime.strptime(END_TIME,
                                                     DATE_FORMAT)), 4)
        mock_slack_client.return_value.chat_postMessage.assert_called_with(channel='C033QBE511V', mrkdown=True, blocks=[
            {'type': 'section', 'text': {'type': 'mrkdwn',
                                         'text': ':warning: *Sentry Errors Usage Alert :sentry::warning:*\n- Usage threshold: 400%\n- Period: 0 day\n- Max usage for period: 2 Errors\n- Errors consumed over period: 1\n- Percentage consumed: 300%'}},
            {'type': 'divider'}, {'type': 'section', 'text': {'type': 'mrkdwn',
                                                              'text': ' Check Sentry for projects reporting excessive errors :eyes:'},
                                  'accessory': {'type': 'button', 'text': {'type': 'plain_text',
                                                                           'text': ':sentry: Error usage for period',
                                                                           'emoji': True},
                                                'url': 'https://ministryofjustice.sentry.io/stats/?dataCategory=errors&end=2023-06-09T00%3A00%3A00Z&sort=-accepted&start=2023-06-08T00%3A00%3A00Z&utc=true'}},
            {'type': 'section',
             'text': {'type': 'mrkdwn', 'text': 'See Sentry usage alert runbook for help with this alert'},
             'accessory': {'type': 'button',
                           'text': {'type': 'plain_text', 'text': ':blue_book: Runbook', 'emoji': True},
                           'url': 'https://operations-engineering.service.justice.gov.uk/documentation/runbooks/internal/respond-to-sentry-usage-alert.html'}}])


@patch("slack_sdk.WebClient.__new__")
class TestSlackServiceSendTransactionUsageAlertToOperationsEngineering(unittest.TestCase):

    def test_downstream_services_called(self, mock_slack_client: MagicMock):
        SlackService("").send_transaction_usage_alert_to_operations_engineering(
            0, UsageStats(1, 2, 3, start_time=datetime.strptime(START_TIME,
                                                                DATE_FORMAT),
                          end_time=datetime.strptime(END_TIME,
                                                     DATE_FORMAT)), 4)
        mock_slack_client.return_value.chat_postMessage.assert_called_with(channel='C033QBE511V', mrkdown=True, blocks=[
            {'type': 'section', 'text': {'type': 'mrkdwn',
                                         'text': ':warning: *Sentry Transactions Usage Alert :sentry::warning:*\n- Usage threshold: 400%\n- Period: 0 day\n- Max usage for period: 2 Transactions\n- Transactions consumed over period: 1\n- Percentage consumed: 300%'}},
            {'type': 'divider'}, {'type': 'section', 'text': {'type': 'mrkdwn',
                                                              'text': 'Check Sentry for projects consuming excessive transactions :eyes:'},
                                  'accessory': {'type': 'button', 'text': {'type': 'plain_text',
                                                                           'text': ':sentry: Transaction usage for period',
                                                                           'emoji': True},
                                                'url': 'https://ministryofjustice.sentry.io/stats/?dataCategory=transactions&end=2023-06-09T00%3A00%3A00Z&sort=-accepted&start=2023-06-08T00%3A00%3A00Z&utc=true'}},
            {'type': 'section',
             'text': {'type': 'mrkdwn', 'text': 'See Sentry usage alert runbook for help with this alert'},
             'accessory': {'type': 'button',
                           'text': {'type': 'plain_text', 'text': ':blue_book: Runbook', 'emoji': True},
                           'url': 'https://operations-engineering.service.justice.gov.uk/documentation/runbooks/internal/respond-to-sentry-usage-alert.html'}}])


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
                        "text": '*Dormants Users Automation*\nRemove these users from the Dormants Users allow list:\n[\'some-user1\', \'some-user2\', \'some-user3\']'
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
                        "text": '*Dormants Users Automation*\nRemoved 3 users from the some-org GitHub Organisation.\nSee the GH Action for more info: https://github.com/ministryofjustice/operations-engineering'
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
                        "text": '*Dormants Users Automation*\nUndelivered emails for some-org GitHub Organisation:\n[\'some-user1@domain.com\', \'some-user2@domain.com\', \'some-user3@domain.com\']\nRemove these users manually'
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
                        "text": '*Dormants Users Automation*\nRemove these users from the Dormants Users allow list:\n[\'some-user1\', \'some-user2\', \'some-user3\']'
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
                        "text": '*Dormants Users Automation*\nRemoved 3 users from the some-org GitHub Organisation.\nSee the GH Action for more info: https://github.com/ministryofjustice/operations-engineering'
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
                        "text": '*Dormants Users Automation*\nUndelivered emails for some-org GitHub Organisation:\n[\'some-user1@domain.com\', \'some-user2@domain.com\', \'some-user3@domain.com\']\nRemove these users manually'
                    }
                }
            ]
        )


if __name__ == "__main__":
    unittest.main()
