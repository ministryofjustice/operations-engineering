import unittest
from unittest.mock import patch, MagicMock

from services.github_service import GithubService
from services.kpi_service import KpiService

from bin.fetch_github_actions_quota import get_environment_variables, fetch_gha_quota


class TestFetchGithubActionsQuota(unittest.TestCase):

    @patch('os.getenv')
    def test_get_environment_variables(self, mock_getenv):

        mock_getenv.return_value = "token_mock"

        result = get_environment_variables()

        self.assertEqual(result, "token_mock")

    @patch('os.getenv')
    def test_get_environment_variables_missing_token(self, mock_getenv):

        mock_getenv.return_value = None

        with self.assertRaises(ValueError) as context:
            get_environment_variables()

        self.assertEqual(str(context.exception), "The env variable GH_TOKEN is empty or missing")

    @patch("gql.transport.aiohttp.AIOHTTPTransport.__new__", new=MagicMock)
    @patch("gql.Client.__new__", new=MagicMock)
    @patch("github.Github.__new__", new=MagicMock)
    @patch("bin.fetch_github_actions_quota.get_environment_variables")
    @patch.object(GithubService, "calculate_total_minutes_enterprise")
    @patch.object(KpiService, "track_enterprise_github_actions_quota_usage")
    def test_fetch_gha_quota(
        self,
        mock_track_enterprise_github_actions_quota_usage,
        mock_calculate_total_minutes_enterprise,
        mock_get_environment_variables
    ):
        # Mock services
        mock_get_environment_variables.return_value = "token_mock"
        mock_calculate_total_minutes_enterprise.return_value = 3456778

        # Run script
        fetch_gha_quota()

        # Assert
        mock_get_environment_variables.assert_called_once()
        mock_calculate_total_minutes_enterprise.assert_called_once()
        mock_track_enterprise_github_actions_quota_usage.assert_called_once_with(3456778)


if __name__ == '__main__':
    unittest.main()
