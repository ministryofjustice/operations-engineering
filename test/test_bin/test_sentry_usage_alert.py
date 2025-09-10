import os
import unittest
from unittest.mock import MagicMock, call, patch

from bin import sentry_usage_alert
from services.sentry_service import UsageStats

START_TIME = "2023-06-08T00:00:00Z"
END_TIME = "2023-06-09T00:00:00Z"


@patch("services.slack_service.SlackService.__new__")
@patch("clients.sentry_client.SentryClient.__new__")
class TestSentryUsageAlertMain(unittest.TestCase):
    @patch.dict(os.environ, {"SENTRY_TOKEN": "token"})
    @patch.dict(os.environ, {"SLACK_TOKEN": "token"})
    def test_main_smoke_test(
        self,
        mock_sentry_client: MagicMock,
        _mock_slack_service: MagicMock,
    ):
        mock_sentry_client.return_value.get_usage_total_for_period_in_days.return_value = (
            1,
            START_TIME,
            END_TIME,
        )
        sentry_usage_alert.main()

    @patch.dict(os.environ, {"SENTRY_TOKEN": "token"})
    @patch.dict(os.environ, {"SLACK_TOKEN": "token"})
    @patch.dict(os.environ, {"PERIOD_IN_DAYS": "1"})
    @patch.dict(os.environ, {"USAGE_THRESHOLD": "20"})
    def test_sends_notifications_to_slack_when_usage_above_threshold(
        self,
        mock_sentry_client: MagicMock,
        mock_slack_service: MagicMock,
    ):
        mock_sentry_client.return_value.get_usage_total_for_period_in_days.return_value = (
            10000000,
            START_TIME,
            END_TIME,
        )
        sentry_usage_alert.main()
        mock_slack_service.return_value.send_usage_alert_to_operations_engineering.assert_has_calls(
            [
                call(
                    1,
                    UsageStats(
                        total=10000000,
                        max_usage=129032,
                        percentage_of_quota_used=77.50015500031,
                        start_time="2023-06-08T00:00:00Z",
                        end_time="2023-06-09T00:00:00Z",
                    ),
                    0.2,
                    "error",
                ),
                call(
                    1,
                    UsageStats(
                        total=10000000,
                        max_usage=967741,
                        percentage_of_quota_used=10.333343322231878,
                        start_time="2023-06-08T00:00:00Z",
                        end_time="2023-06-09T00:00:00Z",
                    ),
                    0.2,
                    "span",
                ),
                call(
                    1,
                    UsageStats(
                        total=10000000,
                        max_usage=25806,
                        percentage_of_quota_used=387.50678136867396,
                        start_time="2023-06-08T00:00:00Z",
                        end_time="2023-06-09T00:00:00Z",
                    ),
                    0.2,
                    "replay",
                ),
            ],
            any_order=False,
        )

    @patch.dict(os.environ, {"SENTRY_TOKEN": "token"})
    @patch.dict(os.environ, {"SLACK_TOKEN": "token"})
    def test_sends_no_notifications_to_slack_when_usage_below_threshold(
        self,
        mock_sentry_client: MagicMock,
        mock_slack_service: MagicMock,
    ):
        mock_sentry_client.return_value.get_usage_total_for_period_in_days.return_value = (
            1,
            START_TIME,
            END_TIME,
        )
        sentry_usage_alert.main()
        mock_slack_service.return_value.send_error_usage_alert_to_operations_engineering.assert_not_called()
        mock_slack_service.return_value.send_span_usage_alert_to_operations_engineering.assert_not_called()

@patch("requests.get", new=MagicMock)
class TestGetEnvironmentVariables(unittest.TestCase):
    def test_raises_error_when_no_sentry_environment_variable_provided(self):
        self.assertRaises(ValueError, sentry_usage_alert.get_environment_variables)

    @patch.dict(os.environ, {"SENTRY_TOKEN": "sentry_token"})
    def test_raises_error_when_no_slack_environment_variable_provided(self):
        self.assertRaises(ValueError, sentry_usage_alert.get_environment_variables)

    @patch.dict(os.environ, {"SLACK_TOKEN": "slack_token"})
    @patch.dict(os.environ, {"SENTRY_TOKEN": "sentry_token"})
    @patch.dict(os.environ, {"PERIOD_IN_DAYS": "1"})
    @patch.dict(os.environ, {"USAGE_THRESHOLD": "20"})
    def test_returns_values(self):
        sentry_token, slack_token, period_in_days, usage_threshold = (
            sentry_usage_alert.get_environment_variables()
        )
        self.assertEqual(sentry_token, "sentry_token")
        self.assertEqual(slack_token, "slack_token")
        self.assertEqual(period_in_days, 1)
        self.assertEqual(usage_threshold, 0.20)


if __name__ == "__main__":
    unittest.main()
