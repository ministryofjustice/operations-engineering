import unittest
from unittest.mock import MagicMock, patch

from python.clients.sentry_client import SentryClient


@patch("requests.get")
class TestSentryClientGetOrganizationStats(unittest.TestCase):

    def test_returns_response_as_json(self, mock_get: MagicMock):
        mock_get.return_value.json.return_value = {"groups": [{"totals": {"sum(quantity)": 100}}]}
        sentry_client = SentryClient("https://test_sentry.com", "test_token")
        response = sentry_client.get_usage_total_for_period_in_days("error", 1)
        self.assertEqual(100, response)

    def test_calls_downstream_services(self, mock_get: MagicMock):
        sentry_client = SentryClient("https://test_sentry.com", "test_token")
        sentry_client.get_usage_total_for_period_in_days("error", 1)
        mock_get.assert_called_with(
            'https://test_sentry.com/api/0/organizations/ministryofjustice/stats_v2/?statsPeriod=1d&field=sum(quantity)&category=error&outcome=accepted',
            headers={'Authorization': 'Bearer test_token'}, timeout=10)


if __name__ == "__main__":
    unittest.main()
