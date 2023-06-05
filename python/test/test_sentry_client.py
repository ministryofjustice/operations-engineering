import unittest
from unittest.mock import MagicMock, Mock, patch

from python.clients.sentry_client import SentryClient


@patch("requests.get")
class TestSentryClientGetOrganizationStatsForOneDay(unittest.TestCase):

    def test_returns_response_as_json(self, mock_get: MagicMock):
        mock_response = Mock(json=Mock())
        mock_get.return_value.json.return_value = mock_response
        sentry_client = SentryClient("https://test_sentry.com", "test_token")
        response = sentry_client.get_organization_stats_for_one_day()
        self.assertEqual(mock_response, response)

    def test_calls_downstream_services(self, mock_get: MagicMock):
        sentry_client = SentryClient("https://test_sentry.com", "test_token")
        sentry_client.get_organization_stats_for_one_day()
        mock_get.assert_called_with(
            'https://test_sentry.com/api/0/organizations/ministryofjustice/stats_v2/?statsPeriod=1d&field=sum(quantity)&groupBy=category',
            headers={'Authorization': 'Bearer test_token'}, timeout=10)


if __name__ == "__main__":
    unittest.main()
