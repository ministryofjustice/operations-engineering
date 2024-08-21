import unittest
from unittest.mock import MagicMock, patch, call

from services.kpi_service import KpiService

TEST_API_KEY = "test_api_key"
TEST_BASE_URL = "test_base_url"


@patch("services.kpi_service.requests")
class TestKPIServiceTrackNumberOfRepositoriesWithStandardsLabel(unittest.TestCase):
    def test_api_called(self, mock_requests: MagicMock):
        KpiService(
            TEST_BASE_URL, TEST_API_KEY
        ).track_number_of_repositories_with_standards_label(1)

        mock_requests.post.assert_has_calls(
            [
                call(
                    url=f"{TEST_BASE_URL}/api/indicator/add",
                    headers={
                        "X-API-KEY": TEST_API_KEY,
                        "Content-Type": "application/json",
                    },
                    timeout=10,
                    json={"indicator": "REPOSITORIES_WITH_STANDARDS_LABEL", "count": 1},
                )
            ]
        )


@patch("services.kpi_service.requests")
class TestKPIServiceTrackSentryTransactionsUsedForDay(unittest.TestCase):
    def test_api_called(self, mock_requests: MagicMock):
        KpiService(TEST_BASE_URL, TEST_API_KEY).track_sentry_transactions_used_for_day(
            1
        )

        mock_requests.post.assert_has_calls(
            [
                call(
                    url=f"{TEST_BASE_URL}/api/indicator/add",
                    headers={
                        "X-API-KEY": TEST_API_KEY,
                        "Content-Type": "application/json",
                    },
                    timeout=10,
                    json={
                        "indicator": "SENTRY_TRANSACTIONS_USED_OVER_PAST_DAY",
                        "count": 1,
                    },
                )
            ]
        )


@patch("services.kpi_service.requests")
class TestKPIServiceTrackSentryErrorsUsedForDay(unittest.TestCase):
    def test_api_called(self, mock_requests: MagicMock):
        KpiService(TEST_BASE_URL, TEST_API_KEY).track_sentry_errors_used_for_day(1)

        mock_requests.post.assert_has_calls(
            [
                call(
                    url=f"{TEST_BASE_URL}/api/indicator/add",
                    headers={
                        "X-API-KEY": TEST_API_KEY,
                        "Content-Type": "application/json",
                    },
                    timeout=10,
                    json={
                        "indicator": "SENTRY_ERRORS_USED_OVER_PAST_DAY",
                        "count": 1,
                    },
                )
            ]
        )


@patch("services.kpi_service.requests")
class TestKPIServiceTrackSentryReplaysUsedForDay(unittest.TestCase):
    def test_api_called(self, mock_requests: MagicMock):
        KpiService(TEST_BASE_URL, TEST_API_KEY).track_sentry_replays_used_for_day(1)

        mock_requests.post.assert_has_calls(
            [
                call(
                    url=f"{TEST_BASE_URL}/api/indicator/add",
                    headers={
                        "X-API-KEY": TEST_API_KEY,
                        "Content-Type": "application/json",
                    },
                    timeout=10,
                    json={
                        "indicator": "SENTRY_REPLAYS_USED_OVER_PAST_DAY",
                        "count": 1,
                    },
                )
            ]
        )


if __name__ == "__main__":
    unittest.main()
