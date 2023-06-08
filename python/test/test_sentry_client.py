import unittest
from unittest.mock import MagicMock, patch

from python.clients.sentry_client import SentryClient

START_TIME = "2023-06-08T00:00:00Z"
END_TIME = "2023-06-09T00:00:00Z"
DATE_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


@patch("requests.get")
class TestSentryClientGetOrganizationStats(unittest.TestCase):

    def test_returns_sum_quantity(self, mock_get: MagicMock):
        mock_get.return_value.json.return_value = {
            "start": START_TIME,
            "end": END_TIME,
            "groups": [{"totals": {"sum(quantity)": 100}}]
        }
        sentry_client = SentryClient("https://test_sentry.com", "test_token")
        total, start_time, end_time = sentry_client.get_usage_total_for_period_in_days(
            "error", 1)
        self.assertEqual(100, total)
        self.assertEqual(START_TIME, start_time.strftime(DATE_FORMAT))
        self.assertEqual(END_TIME, end_time.strftime(DATE_FORMAT))

    def test_calls_downstream_services(self, mock_get: MagicMock):
        mock_get.return_value.json.return_value = {
            "start": START_TIME,
            "end": END_TIME,
            "groups": [{"totals": {"sum(quantity)": 100}}]
        }
        sentry_client = SentryClient("https://test_sentry.com", "test_token")
        sentry_client.get_usage_total_for_period_in_days("error", 1)
        mock_get.assert_called_with(
            'https://test_sentry.com/api/0/organizations/ministryofjustice/stats_v2/?statsPeriod=1d&field=sum(quantity)&category=error&outcome=accepted',
            headers={'Authorization': 'Bearer test_token'}, timeout=10)


if __name__ == "__main__":
    unittest.main()
