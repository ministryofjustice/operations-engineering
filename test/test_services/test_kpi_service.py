import unittest
from unittest.mock import MagicMock, patch, call

from services.kpi_service import KpiService

TEST_API_KEY = "test_api_key"
TEST_BASE_URL = "test_base_url"

@patch("services.kpi_service.requests")
class TestKPIServiceTrackEnterpriceGithubActionQuotaUsage(unittest.TestCase):
    def test_api_called(self, mock_requests: MagicMock):
        KpiService(TEST_BASE_URL, TEST_API_KEY).track_enterprise_github_actions_quota_usage(1)

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
                        "indicator": "ENTERPRISE_GITHUB_ACTIONS_QUOTA_USAGE",
                        "count": 1,
                    },
                )
            ]
        )


if __name__ == "__main__":
    unittest.main()
