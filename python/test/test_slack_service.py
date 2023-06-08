import unittest
from unittest.mock import MagicMock, patch

from python.services.sentry_service import UsageStats
from python.services.slack_service import SlackService


@patch("slack_sdk.WebClient.__new__")
class TestSlackServiceInit(unittest.TestCase):

    def test_sets_up_class(self, mock_slack_client: MagicMock):
        mock_slack_client.return_value = "test_mock"
        slack_service = SlackService("")
        self.assertEqual("test_mock",
                         slack_service.slack_client)


@patch("slack_sdk.WebClient.__new__")
class TestSlackServiceSendErrorUsageAlertToOperationsEngineering(unittest.TestCase):

    def test_downstream_services_called(self, mock_slack_client: MagicMock):
        SlackService("").send_error_usage_alert_to_operations_engineering(
            0, UsageStats(1, 2, 3), 4)
        mock_slack_client.return_value.chat_postMessage.assert_called_with(channel='C033QBE511V', mrkdown=True, blocks=[
            {'type': 'section', 'text': {'type': 'mrkdwn',
                                         'text': ':sentry: *Sentry Errors Usage Alert :warning:*\n- Usage threshold: 400%\n- Period: 0 day\n- Max usage for period: 2 Errors\n- Errors consumed over period: 1\n- Percentage consumed: 300%'}},
            {'type': 'divider'},
            {'type': 'section', 'text': {'type': 'mrkdwn', 'text': ' Check Sentry for Spikes :eyes:'},
             'accessory': {'type': 'button',
                           'text': {'type': 'plain_text', 'text': ':sentry: Error Usage For Period', 'emoji': True},
                           'url': 'https://ministryofjustice.sentry.io/stats/?dataCategory=errors&statsPeriod=0d'}}])


@patch("slack_sdk.WebClient.__new__")
class TestSlackServiceSendTransactionUsageAlertToOperationsEngineering(unittest.TestCase):

    def test_downstream_services_called(self, mock_slack_client: MagicMock):
        SlackService("").send_transaction_usage_alert_to_operations_engineering(
            0, UsageStats(1, 2, 3), 4)
        mock_slack_client.return_value.chat_postMessage.assert_called_with(channel='C033QBE511V', mrkdown=True, blocks=[
            {'type': 'section', 'text': {'type': 'mrkdwn',
                                         'text': ':sentry: *Sentry Transactions Usage Alert :warning:*\n- Usage threshold: 400%\n- Period: 0 day\n- Max usage for period: 2 Transactions\n- Transactions consumed over period: 1\n- Percentage consumed: 300%'}},
            {'type': 'divider'},
            {'type': 'section', 'text': {'type': 'mrkdwn', 'text': ' Check Sentry for Spikes :eyes:'},
             'accessory': {'type': 'button',
                           'text': {'type': 'plain_text', 'text': ':sentry: Transaction Usage For Period',
                                    'emoji': True},
                           'url': 'https://ministryofjustice.sentry.io/stats/?dataCategory=transactions&statsPeriod=0d'}}])


if __name__ == "__main__":
    unittest.main()
