import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch

from services.sentry_service import UsageStats
from services.slack_service import SlackService

START_TIME = "2023-06-08T00:00:00Z"
END_TIME = "2023-06-09T00:00:00Z"
DATE_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
SENTRY_QUOTA_MANAGEMENT_GUIDANCE = "https://runbooks.operations-engineering.service.justice.gov.uk/documentation/services/sentryio/respond-to-sentry-usage-alert"


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

    def test_send_message_to_plaintext_channel_name(self):
        self.slack_client.chat_postMessage.return_value = self.response
        self.slack_service.send_message_to_plaintext_channel_name(
            self.message, self.channel_name)
        self.slack_client.chat_postMessage.assert_called_once_with(
            channel=self.channel_id, text=self.message)

    def test_send_message_to_plaintext_channel_name_when_no_channel_name_exists(self):
        response = {'channels': [],
                    'response_metadata': self.response_metadata}
        self.slack_client.conversations_list.return_value = response
        self.slack_service.send_message_to_plaintext_channel_name(
            self.message, self.channel_name)
        self.slack_client.chat_postMessage.assert_not_called()

    def test_send_message_to_plaintext_channel_name_when_response_not_okay(self):
        response = {'ok': False, "error": "some-error"}
        self.slack_client.chat_postMessage.return_value = response
        self.slack_service.send_message_to_plaintext_channel_name(
            self.message, self.channel_name)
        self.slack_client.chat_postMessage.assert_called_once_with(
            channel=self.channel_id, text=self.message)

    def test_lookup_channel_id(self):
        result = self.slack_service._lookup_channel_id(self.channel_name)
        self.slack_client.conversations_list.assert_called_once_with(
            limit=200, cursor='')
        self.assertEqual(result, self.channel_id)

    def test_lookup_channel_id_when_no_matching_channels(self):
        response = {'channels': [
            {'name': "other-channel", 'id': self.channel_id}], 'response_metadata': self.response_metadata}
        self.slack_client.conversations_list.return_value = response
        result = self.slack_service._lookup_channel_id(self.channel_name)
        self.slack_client.conversations_list.assert_called_once_with(
            limit=200, cursor='')
        self.assertIsNone(result)

    def test_lookup_channel_id_when_channels_empty(self):
        response = {'channels': [],
                    'response_metadata': self.response_metadata}
        self.slack_client.conversations_list.return_value = response
        result = self.slack_service._lookup_channel_id(self.channel_name)
        self.slack_client.conversations_list.assert_called_once_with(
            limit=200, cursor='')
        self.assertIsNone(result)

    def test_lookup_channel_id_when_no_channels(self):
        response = {'channels': None,
                    'response_metadata': self.response_metadata}
        self.slack_client.conversations_list.return_value = response
        result = self.slack_service._lookup_channel_id(self.channel_name)
        self.slack_client.conversations_list.assert_called_once_with(
            limit=200, cursor='')
        self.assertIsNone(result)


@patch("slack_sdk.WebClient.__new__")
class TestSlackServiceSendErrorUsageAlertToOperationsEngineering(unittest.TestCase):

    def test_downstream_services_called(self, mock_slack_client: MagicMock):
        SlackService("").send_usage_alert_to_operations_engineering(
            0,
            UsageStats(
                1,
                2,
                3,
                start_time=datetime.strptime(START_TIME, DATE_FORMAT),
                end_time=datetime.strptime(END_TIME, DATE_FORMAT)
            ),
            4,
            "error"
        )
        mock_slack_client.return_value.chat_postMessage.assert_called_with(channel='C033QBE511V', mrkdown=True, blocks=[
            {'type': 'section', 'text': {'type': 'mrkdwn',
                                         'text': ':warning: *Sentry Error Usage Alert :sentry::warning:*\n- Usage threshold: 400%\n- Period: 0 day\n- Max usage for period: 2 Errors\n- Errors consumed over period: 1\n- Percentage consumed: 300%'}},
            {'type': 'divider'}, {'type': 'section', 'text': {'type': 'mrkdwn',
                                                              'text': 'Check Sentry for projects with excessive errors :eyes:'},
                                  'accessory': {'type': 'button', 'text': {'type': 'plain_text',
                                                                           'text': ':sentry: Error usage for period',
                                                                           'emoji': True},
                                                'url': 'https://ministryofjustice.sentry.io/stats/?dataCategory=errors&end=2023-06-09T00%3A00%3A00Z&sort=-accepted&start=2023-06-08T00%3A00%3A00Z&utc=true'}},
            {'type': 'section',
             'text': {'type': 'mrkdwn', 'text': 'See Sentry usage alert runbook for help with this alert'},
             'accessory': {'type': 'button',
                           'text': {'type': 'plain_text', 'text': ':blue_book: Runbook', 'emoji': True},
                           'url': SENTRY_QUOTA_MANAGEMENT_GUIDANCE}}])


@patch("slack_sdk.WebClient.__new__")
class TestSlackServiceSendTransactionUsageAlertToOperationsEngineering(unittest.TestCase):

    def test_downstream_services_called(self, mock_slack_client: MagicMock):
        SlackService("").send_usage_alert_to_operations_engineering(
            0,
            UsageStats(
                1,
                2,
                3,
                start_time=datetime.strptime(START_TIME, DATE_FORMAT),
                end_time=datetime.strptime(END_TIME, DATE_FORMAT)
            ),
            4,
            "transaction"
        )
        mock_slack_client.return_value.chat_postMessage.assert_called_with(channel='C033QBE511V', mrkdown=True, blocks=[
            {'type': 'section', 'text': {'type': 'mrkdwn',
                                         'text': ':warning: *Sentry Transaction Usage Alert :sentry::warning:*\n- Usage threshold: 400%\n- Period: 0 day\n- Max usage for period: 2 Transactions\n- Transactions consumed over period: 1\n- Percentage consumed: 300%'}},
            {'type': 'divider'}, {'type': 'section', 'text': {'type': 'mrkdwn',
                                                              'text': 'Check Sentry for projects with excessive transactions :eyes:'},
                                  'accessory': {'type': 'button', 'text': {'type': 'plain_text',
                                                                           'text': ':sentry: Transaction usage for period',
                                                                           'emoji': True},
                                                'url': 'https://ministryofjustice.sentry.io/stats/?dataCategory=transactions&end=2023-06-09T00%3A00%3A00Z&sort=-accepted&start=2023-06-08T00%3A00%3A00Z&utc=true'}},
            {'type': 'section',
             'text': {'type': 'mrkdwn', 'text': 'See Sentry usage alert runbook for help with this alert'},
             'accessory': {'type': 'button',
                           'text': {'type': 'plain_text', 'text': ':blue_book: Runbook', 'emoji': True},
                           'url': SENTRY_QUOTA_MANAGEMENT_GUIDANCE}}])


@patch("slack_sdk.WebClient.__new__")
class TestSlackServiceSendReplayUsageAlertToOperationsEngineering(unittest.TestCase):

    def test_downstream_services_called(self, mock_slack_client: MagicMock):
        SlackService("").send_usage_alert_to_operations_engineering(
            0,
            UsageStats(
                1,
                2,
                3,
                start_time=datetime.strptime(START_TIME, DATE_FORMAT),
                end_time=datetime.strptime(END_TIME, DATE_FORMAT)
            ),
            4,
            "replay"
        )
        mock_slack_client.return_value.chat_postMessage.assert_called_with(channel='C033QBE511V', mrkdown=True, blocks=[
            {'type': 'section', 'text': {'type': 'mrkdwn',
                                         'text': ':warning: *Sentry Replay Usage Alert :sentry::warning:*\n- Usage threshold: 400%\n- Period: 0 day\n- Max usage for period: 2 Replays\n- Replays consumed over period: 1\n- Percentage consumed: 300%'}},
            {'type': 'divider'}, {'type': 'section', 'text': {'type': 'mrkdwn',
                                                              'text': 'Check Sentry for projects with excessive replays :eyes:'},
                                  'accessory': {'type': 'button', 'text': {'type': 'plain_text',
                                                                           'text': ':sentry: Replay usage for period',
                                                                           'emoji': True},
                                                'url': 'https://ministryofjustice.sentry.io/stats/?dataCategory=replays&end=2023-06-09T00%3A00%3A00Z&sort=-accepted&start=2023-06-08T00%3A00%3A00Z&utc=true'}},
            {'type': 'section',
             'text': {'type': 'mrkdwn', 'text': 'See Sentry usage alert runbook for help with this alert'},
             'accessory': {'type': 'button',
                           'text': {'type': 'plain_text', 'text': ':blue_book: Runbook', 'emoji': True},
                           'url': SENTRY_QUOTA_MANAGEMENT_GUIDANCE}}])


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


@patch("slack_sdk.WebClient.__new__")
class SendUnownedReposAlertToOperationsEngineering(unittest.TestCase):

    def test_downstream_services_called(self, mock_slack_client: MagicMock):
        repos = ["some-repo1", "some-repo2", "some-repo3"]
        SlackService(
            "").send_unowned_repos_slack_message(repos)
        mock_slack_client.return_value.chat_postMessage.assert_called_with(
            channel="C033QBE511V",
            mrkdown=True,
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": '*Unowned Repositories Automation*\nRepositories on the GitHub Organisation that have no team or collaborator:\n[\'some-repo1\', \'some-repo2\', \'some-repo3\']'
                    }
                }
            ]
        )


@patch('slack_sdk.WebClient.users_list')
class GetAllSlackUsernamesTest(unittest.TestCase):

    @patch("slack_sdk.WebClient")
    def setUp(self, mock_web_client):
        self.mock_web_client = mock_web_client
        self.slack_service = SlackService("")

    def test_get_all_slack_usernames_success(self, mock_users_list):
        mock_response = {
            'ok': True,
            'members': [{'name': 'user1', 'profile': {'email': 'user1@example.com'}},
                        {'name': 'user2', 'profile': {'email': 'user2@example.com'}}],
            'response_metadata': {'next_cursor': ''}
        }

        mock_users_list.return_value = mock_response

        result = self.slack_service.get_all_slack_usernames()

        self.assertEqual(result, [
            {'username': 'user1', 'email': 'user1@example.com'},
            {'username': 'user2', 'email': 'user2@example.com'}
        ])

    def test_handle_api_error_gracefully(self, mock_user_list):
        mock_response = {
            'ok': False,
            'error': 'error'
        }

        mock_user_list.return_value = mock_response

        result = self.slack_service.get_all_slack_usernames()

        self.assertEqual(result, [])

    def test_handle_exception_gracefully(self, mock_user_list):
        mock_user_list.side_effect = Exception("An unexpected error occurred")

        result = self.slack_service.get_all_slack_usernames()

        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()
