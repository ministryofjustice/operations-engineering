import unittest
from unittest.mock import patch, MagicMock

from bin.alert_on_low_github_actions_quota import (
    alert_on_low_quota
)

from services.github_service import GithubService
from services.slack_service import SlackService


class TestGithubACtionsQuotaAlerting(unittest.TestCase):

    @patch("gql.transport.aiohttp.AIOHTTPTransport.__new__", new=MagicMock)
    @patch("gql.Client.__new__", new=MagicMock)
    @patch("github.Github.__new__")
    @patch.object(GithubService, "modify_gha_minutes_quota_threshold")
    @patch.object(SlackService, "send_low_github_actions_quota_alert")
    @patch.object(GithubService, "check_if_gha_minutes_quota_is_low")
    @patch("os.environ.get")
    def test_alert_on_low_quota_if_low(
        self,
        mock_get_env,
        mock_check_if_gha_minutes_quota_is_low,
        mock_send_low_github_actions_quota_alert,
        mock_modify_gha_minutes_quota_threshold,
        _mock_github_client_core_api
    ):
        mock_get_env.side_effect = lambda k: 'mock_token' if k in ['GH_TOKEN', 'ADMIN_SLACK_TOKEN'] else None
        mock_check_if_gha_minutes_quota_is_low.return_value = {'threshold': 70, 'percentage_used': 75}

        alert_on_low_quota()

        mock_check_if_gha_minutes_quota_is_low.assert_called_once()
        mock_send_low_github_actions_quota_alert.assert_called_once_with(75)
        mock_modify_gha_minutes_quota_threshold.assert_called_once_with(80)

    @patch("gql.transport.aiohttp.AIOHTTPTransport.__new__", new=MagicMock)
    @patch("gql.Client.__new__", new=MagicMock)
    @patch("github.Github.__new__")
    @patch.object(GithubService, "modify_gha_minutes_quota_threshold")
    @patch.object(SlackService, "send_low_github_actions_quota_alert")
    @patch.object(GithubService, "check_if_gha_minutes_quota_is_low")
    @patch('os.environ')
    def test_alert_on_low_quota_if_not_low(
        self,
        mock_env,
        mock_check_if_gha_minutes_quota_is_low,
        mock_send_low_github_actions_quota_alert,
        mock_modify_gha_minutes_quota_threshold,
        _mock_github_client_core_api
    ):

        mock_env.get.side_effect = lambda k: 'mock_token' if k in ['GH_TOKEN', 'ADMIN_SLACK_TOKEN'] else None
        mock_check_if_gha_minutes_quota_is_low.return_value = False

        alert_on_low_quota()

        mock_check_if_gha_minutes_quota_is_low.assert_called_once()
        assert not mock_send_low_github_actions_quota_alert.called
        assert not mock_modify_gha_minutes_quota_threshold.called


if __name__ == '__main__':
    unittest.main()
