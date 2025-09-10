import unittest
from unittest.mock import Mock, patch

from services.sentry_service import SentryService


@patch("clients.sentry_client.SentryClient.__new__")
class TestSentryServiceLogQuotaUsageForPeriodInDays(unittest.TestCase):
    def test_returns_values(self, mock_sentry_client: Mock):
        mock_sentry_client.get_usage_total_for_period_in_days.return_value = 10000, "2023-06-08T00:00:00Z", "2023-06-09T00:00:00Z"

        error_usage_stats, span_usage_stats, replay_usage_stats = SentryService(mock_sentry_client).get_quota_usage_for_period_in_days(1)

        self.assertEqual(10000, error_usage_stats.total)
        self.assertEqual("2023-06-08T00:00:00Z", error_usage_stats.start_time)
        self.assertEqual("2023-06-09T00:00:00Z", error_usage_stats.end_time)
        self.assertEqual(0.08, round(error_usage_stats.percentage_of_quota_used, 2))
        self.assertEqual(129032, error_usage_stats.max_usage)

        self.assertEqual(10000, span_usage_stats.total)
        self.assertEqual(0.01, round(span_usage_stats.percentage_of_quota_used, 2))
        self.assertEqual(1000000, span_usage_stats.max_usage)

        self.assertEqual(10000, replay_usage_stats.total)
        self.assertEqual(0.39, round(replay_usage_stats.percentage_of_quota_used, 2))
        self.assertEqual(25806, replay_usage_stats.max_usage)


if __name__ == "__main__":
    unittest.main()
