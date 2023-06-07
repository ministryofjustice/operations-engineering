import os
import unittest
from unittest.mock import MagicMock, patch

from python.scripts import sentry_usage_alert
from python.services.sentry_service import UsageStats


@patch("python.services.slack_service.SlackService.__new__")
@patch("python.clients.sentry_client.SentryClient.__new__")
class TestSentryUsageAlertMain(unittest.TestCase):

    @patch.dict(os.environ, {"SENTRY_TOKEN": "token"})
    @patch.dict(os.environ, {"SLACK_TOKEN": "token"})
    def test_main_smoke_test(self, mock_sentry_client: MagicMock, mock_slack_service: MagicMock):
        mock_sentry_client.return_value.get_usage_total_for_period_in_days.return_value = 1
        sentry_usage_alert.main()

    @patch.dict(os.environ, {"SENTRY_TOKEN": "token"})
    @patch.dict(os.environ, {"SLACK_TOKEN": "token"})
    def test_sends_notifications_to_slack_when_usage_above_threshold(self, mock_sentry_client: MagicMock,
                                                                     mock_slack_service: MagicMock):
        mock_sentry_client.return_value.get_usage_total_for_period_in_days.return_value = 10000000
        sentry_usage_alert.main()
        mock_slack_service.return_value \
            .send_error_usage_alert_to_operations_engineering \
            .assert_called_with(1, UsageStats(total=10000000,
                                              max_usage=129032,
                                              percentage_of_quota_used=77.50015500031), 0.2)
        mock_slack_service.return_value \
            .send_transaction_usage_alert_to_operations_engineering. \
            assert_called_with(1, UsageStats(total=10000000,
                                             max_usage=967741,
                                             percentage_of_quota_used=10.333343322231878), 0.2)

    @patch.dict(os.environ, {"SENTRY_TOKEN": "token"})
    @patch.dict(os.environ, {"SLACK_TOKEN": "token"})
    def test_sends_no_notifications_to_slack_when_usage_below_threshold(self, mock_sentry_client: MagicMock,
                                                                        mock_slack_service: MagicMock):
        mock_sentry_client.return_value.get_usage_total_for_period_in_days.return_value = 1
        sentry_usage_alert.main()
        mock_slack_service.return_value.send_error_usage_alert_to_operations_engineering.assert_not_called()
        mock_slack_service.return_value.send_transaction_usage_alert_to_operations_engineering.assert_not_called()


@patch("requests.get", new=MagicMock)
class TestGetEnvironmentVariables(unittest.TestCase):
    def test_raises_error_when_no_environment_variables_provided(self):
        self.assertRaises(
            ValueError, sentry_usage_alert.get_environment_variables)

    @patch.dict(os.environ, {"SLACK_TOKEN": "slack_token"})
    @patch.dict(os.environ, {"SENTRY_TOKEN": "sentry_token"})
    def test_returns_values(self):
        sentry_token, slack_token = sentry_usage_alert.get_environment_variables()
        self.assertEqual(sentry_token, "sentry_token")
        self.assertEqual(slack_token, "slack_token")


if __name__ == "__main__":
    unittest.main()
