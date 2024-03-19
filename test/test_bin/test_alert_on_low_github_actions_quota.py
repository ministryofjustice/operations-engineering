import unittest
from unittest.mock import patch, MagicMock

from bin.alert_on_low_github_actions_quota import (
    low_threshold_triggered_message,
    alert_on_low_quota
)

from services.github_service import GithubService
from services.slack_service import SlackService


class TestGithubACtionsQuotaAlerting(unittest.TestCase):

    def test_low_threshold_triggered_message(self):

        self.assertEqual(low_threshold_triggered_message(10), "Warning:\n\n 90% of the Github Actions minutes quota remains.\n\n What to do next: https://runbooks.operations-engineering.service.justice.gov.uk/documentation/internal/low-github-actions-minutes-procedure.html#low-github-actions-minutes-procedure")

    @patch("gql.transport.aiohttp.AIOHTTPTransport.__new__", new=MagicMock)
    @patch("gql.Client.__new__", new=MagicMock)
    @patch("github.Github.__new__")
    @patch("bin.alert_on_low_github_actions_quota.low_threshold_triggered_message")
    @patch.object(GithubService, "modify_gha_minutes_quota_threshold")
    @patch.object(SlackService, "send_message_to_plaintext_channel_name")
    @patch.object(GithubService, "check_if_gha_minutes_quota_is_low")
    @patch('os.environ')
    def test_alert_on_low_quota_if_low(
        self,
        mock_env,
        mock_check_if_gha_minutes_quota_is_low,
        mock_send_message_to_plaintext_channel_name,
        mock_modify_gha_minutes_quota_threshold,
        mock_low_threshold_triggered_message,
        _mock_github_client_core_api
    ):

        mock_env.get.side_effect = lambda k: 'mock_token' if k in ['GH_TOKEN', 'ADMIN_SLACK_TOKEN'] else None
        mock_check_if_gha_minutes_quota_is_low.return_value = {'threshold': 70, 'percentage_used': 75}
        mock_low_threshold_triggered_message.return_value = "Warning:\n\n 25% of the Github Actions minutes quota remains.\n\n What to do next: https://runbooks.operations-engineering.service.justice.gov.uk/documentation/internal/low-github-actions-minutes-procedure.html#low-github-actions-minutes-procedure"

        alert_on_low_quota()

        mock_check_if_gha_minutes_quota_is_low.assert_called_once()
        mock_send_message_to_plaintext_channel_name.assert_called_once_with("Warning:\n\n 25% of the Github Actions minutes quota remains.\n\n What to do next: https://runbooks.operations-engineering.service.justice.gov.uk/documentation/internal/low-github-actions-minutes-procedure.html#low-github-actions-minutes-procedure", "operations-engineering-alerts")
        mock_modify_gha_minutes_quota_threshold.assert_called_once_with(80)

    @patch("gql.transport.aiohttp.AIOHTTPTransport.__new__", new=MagicMock)
    @patch("gql.Client.__new__", new=MagicMock)
    @patch("github.Github.__new__")
    @patch.object(GithubService, "modify_gha_minutes_quota_threshold")
    @patch.object(SlackService, "send_message_to_plaintext_channel_name")
    @patch.object(GithubService, "check_if_gha_minutes_quota_is_low")
    @patch('os.environ')
    def test_alert_on_low_quota_if_not_low(
        self,
        mock_env,
        mock_check_if_gha_minutes_quota_is_low,
        mock_send_message_to_plaintext_channel_name,
        mock_modify_gha_minutes_quota_threshold,
        _mock_github_client_core_api
    ):

        mock_env.get.side_effect = lambda k: 'mock_token' if k in ['GH_TOKEN', 'ADMIN_SLACK_TOKEN'] else None
        mock_check_if_gha_minutes_quota_is_low.return_value = False

        alert_on_low_quota()

        mock_check_if_gha_minutes_quota_is_low.assert_called_once()
        assert not mock_send_message_to_plaintext_channel_name.called
        assert not mock_modify_gha_minutes_quota_threshold.called


if __name__ == '__main__':
    unittest.main()
