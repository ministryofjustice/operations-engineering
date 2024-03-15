import unittest
from unittest.mock import patch, MagicMock

from bin.alert_on_low_github_actions_quota import (
    calculate_percentage_used,
    low_threshold_triggered_message,
    alert_on_low_quota 
)

from services.github_service import GithubService
from services.slack_service import SlackService


class TestGithubACtionsQuotaAlerting(unittest.TestCase):

    def test_calculate_percentage_used(self):

        self.assertEqual(calculate_percentage_used(5000), 10)

    def test_low_threshold_triggered_message(self):

        self.assertEqual(low_threshold_triggered_message(10), f"Warning:\n\n 90% of the Github Actions minutes quota remains.")

    @patch("gql.transport.aiohttp.AIOHTTPTransport.__new__", new=MagicMock)
    @patch("gql.Client.__new__", new=MagicMock)
    @patch("github.Github.__new__")
    @patch("bin.alert_on_low_github_actions_quota.low_threshold_triggered_message")
    @patch.object(GithubService, "modify_gha_minutes_quota_threshold")
    @patch.object(SlackService, "send_message_to_plaintext_channel_name")
    @patch.object(GithubService, "get_gha_minutes_quota_threshold")
    @patch("bin.alert_on_low_github_actions_quota.reset_alerting_threshold_if_first_day_of_month")
    @patch("bin.alert_on_low_github_actions_quota.calculate_percentage_used")
    @patch("bin.alert_on_low_github_actions_quota.calculate_total_minutes_used")
    @patch.object(GithubService, "get_all_organisations_in_enterprise")
    def test_alert_on_low_quota_if_low(self, 
        mock_get_all_organisations_in_enterprise, 
        mock_calculate_total_minutes_used, 
        mock_calculate_percentage_used, 
        mock_reset_alerting_threshold_if_first_day_of_month,
        mock_get_gha_minutes_quota_threshold, 
        mock_send_message_to_plaintext_channel_name,
        mock_modify_gha_minutes_quota_threshold,
        mock_low_threshold_triggered_message,
        mock_github_client_core_api
    ):

        mock_get_all_organisations_in_enterprise.return_value = ["org1", "org2"]
        mock_calculate_total_minutes_used.return_value = 37500
        mock_calculate_percentage_used.return_value = 75
        mock_get_gha_minutes_quota_threshold.return_value = 70
        mock_low_threshold_triggered_message.return_value = f"Warning:\n\n 25% of the Github Actions minutes quota remains."

        alert_on_low_quota()

        mock_reset_alerting_threshold_if_first_day_of_month.assert_called_once()
        mock_send_message_to_plaintext_channel_name.assert_called_once_with(f"Warning:\n\n 25% of the Github Actions minutes quota remains.", "operations-engineering-alerts")
        mock_modify_gha_minutes_quota_threshold.assert_called_once_with(80)

    @patch("gql.transport.aiohttp.AIOHTTPTransport.__new__", new=MagicMock)
    @patch("gql.Client.__new__", new=MagicMock)
    @patch("github.Github.__new__")
    @patch.object(GithubService, "modify_gha_minutes_quota_threshold")
    @patch.object(SlackService, "send_message_to_plaintext_channel_name")
    @patch.object(GithubService, "get_gha_minutes_quota_threshold")
    @patch("bin.alert_on_low_github_actions_quota.reset_alerting_threshold_if_first_day_of_month")
    @patch("bin.alert_on_low_github_actions_quota.calculate_percentage_used")
    @patch("bin.alert_on_low_github_actions_quota.calculate_total_minutes_used")
    @patch.object(GithubService, "get_all_organisations_in_enterprise")
    def test_alert_on_low_quota_if_not_low(self, 
        mock_get_all_organisations_in_enterprise, 
        mock_calculate_total_minutes_used, 
        mock_calculate_percentage_used, 
        mock_reset_alerting_threshold_if_first_day_of_month,
        mock_get_gha_minutes_quota_threshold, 
        mock_send_message_to_plaintext_channel_name,
        mock_modify_gha_minutes_quota_threshold,
        mock_github_client_core_api
    ):

        mock_get_all_organisations_in_enterprise.return_value = ["org1", "org2"]
        mock_calculate_total_minutes_used.return_value = 5000
        mock_calculate_percentage_used.return_value = 10
        mock_get_gha_minutes_quota_threshold.return_value = 70

        alert_on_low_quota()

        mock_reset_alerting_threshold_if_first_day_of_month.assert_called_once()
        assert not mock_send_message_to_plaintext_channel_name.called
        assert not mock_modify_gha_minutes_quota_threshold.called
        
if __name__ == '__main__':
    unittest.main()
