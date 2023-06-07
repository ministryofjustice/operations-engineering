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
        SlackService("").send_error_usage_alert_to_operations_engineering(0, UsageStats(1, 2, 3), 4)
        mock_slack_client.return_value.chat_postMessage.assert_called_with(channel="C033QBE511V", mrkdown=True,
                                                                           text="*Sentry Errors have exceeded 400.00% usage in the past 0 days*\n`This is a test message for Sentry Error alerts!` :test_tube:\nError quota consumed over past 0 days [ 1 / 2 ]\nPercentage consumed: [ 300.00% ]")


@patch("slack_sdk.WebClient.__new__")
class TestSlackServiceSendTransactionUsageAlertToOperationsEngineering(unittest.TestCase):

    def test_downstream_services_called(self, mock_slack_client: MagicMock):
        SlackService("").send_transaction_usage_alert_to_operations_engineering(0, UsageStats(1, 2, 3), 4)
        mock_slack_client.return_value.chat_postMessage.assert_called_with(channel="C033QBE511V", mrkdown=True,
                                                                           text="*Sentry Transactions have exceeded 400.00% usage in the past 0 days*\n`This is a test message for Sentry Transactions alerts!` :test_tube:\nTransaction quota consumed over past 0 days [ 1 / 2 ]\nPercentage consumed: [ 300.00% ]")


if __name__ == "__main__":
    unittest.main()
