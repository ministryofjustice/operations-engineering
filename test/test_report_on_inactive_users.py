import os
import unittest
from unittest.mock import Mock, patch, MagicMock

import bin.report_on_inactive_users as report_test
from services.github_service import GithubService
from services.slack_service import SlackService


class TestReportOnInactiveUsers(unittest.TestCase):

    @patch("services.slack_service.SlackService")
    @patch("services.github_service.GithubService")
    def setUp(self, mock_github_service, mock_slack_service) -> None:
        if "ADMIN_GITHUB_TOKEN" in os.environ:
            os.environ.pop("ADMIN_GITHUB_TOKEN")
        if "ADMIN_SLACK_TOKEN" in os.environ:
            os.environ.pop("ADMIN_SLACK_TOKEN")

        self.config = {
            "github_team": "github_team",
            "slack_channel": "slack_channel",
            "remove_from_team": True,
            "users_to_ignore": ["user1", "user2"],
            "repositories_to_ignore": ["repo1", "repo2"]
        }

        self.teams = [('some_team', self.config)]
        self.mock_github_service = mock_github_service
        self.mock_slack_service = mock_slack_service
        self.mock_github_service.get_inactive_users.return_value = [
            "some-value"]
        self.user1 = Mock()
        self.user1.login = "user1"
        self.user2 = Mock()
        self.user2.login = "user2"
        self.users = [self.user1, self.user2]
        self.team_name = "team1"
        self.inactivity_months = 1
        self.remove = True

    @patch.dict(os.environ, {"ADMIN_GITHUB_TOKEN": "token", "ADMIN_SLACK_TOKEN": "token"})
    def test_get_environment_variables(self):
        check1, check2 = report_test.get_environment_variables()
        self.assertEqual(check1, "token")
        self.assertEqual(check2, "token")

    @patch.dict(os.environ, {"ADMIN_GITHUB_TOKEN": "token"})
    def test_unset_slack_environment_variables(self):
        self.assertRaises(ValueError, report_test.get_environment_variables)

    @patch.dict(os.environ, {"ADMIN_SLACK_TOKEN": "token"})
    def test_unset_github_environment_variables(self):
        self.assertRaises(ValueError, report_test.get_environment_variables)

    def test_craft_message_for_removed_users(self):
        message = report_test._message_to_users(
            self.users, self.remove, self.team_name, self.inactivity_months)
        self.assertIn("user1", message)
        self.assertIn("1 months", message)
        self.assertIn("team1", message)

    def test_craft_message_to_remove_users(self):
        self.remove = False
        message = report_test._message_to_users(
            self.users, self.remove, self.team_name, self.inactivity_months)
        self.assertIn("user1", message)
        self.assertIn("1 months", message)
        self.assertIn("team1", message)

    def test_craft_message_to_users_no_users(self):
        self.users = []
        message = report_test._message_to_users(
            self.users, self.remove, self.team_name, self.inactivity_months)
        self.assertEqual(message, "")

    def test_load_team_config(self):
        team = report_test._load_team_config(self.config)
        self.assertEqual('github_team', team.github_team)
        self.assertEqual(True, team.remove_users)
        self.assertEqual('slack_channel', team.slack_channel)

    def test_load_team_config_removes_hash_in_slack_channel_name(self):
        self.config["slack_channel"] = "#slack_channel"
        team = report_test._load_team_config(self.config)
        self.assertEqual('slack_channel', team.slack_channel)

    def test_get_config(self):
        org_name, inactivity, teams = report_test.get_config(
            './test/files/test-inactive-users.toml')
        self.assertEqual(org_name, "some-org")
        self.assertEqual(inactivity, 18)
        self.assertEqual(len(teams), 1)

    def test_create_report_dont_remove_users(self):
        report_test._message_to_users = MagicMock()
        self.config["remove_from_team"] = False
        report_test.create_report(
            self.mock_github_service, self.mock_slack_service, 18, self.teams)
        self.mock_github_service.get_inactive_users.assert_called()
        self.mock_github_service.remove_list_of_users_from_team.assert_not_called()
        self.mock_slack_service.send_message_to_plaintext_channel_name.assert_called()

    def test_create_report_happy_path(self):
        report_test._message_to_users = MagicMock()
        report_test.create_report(
            self.mock_github_service, self.mock_slack_service, 18, self.teams)
        self.mock_github_service.get_inactive_users.assert_called()
        self.mock_github_service.remove_list_of_users_from_team.assert_called()
        self.mock_slack_service.send_message_to_plaintext_channel_name.assert_called()

    def test_create_report_dont_send_slack_message(self):
        self.mock_github_service.get_inactive_users.return_value = []
        report_test._message_to_users = MagicMock()
        report_test.create_report(
            self.mock_github_service, self.mock_slack_service, 18, self.teams)
        self.mock_github_service.get_inactive_users.assert_called()
        self.mock_github_service.remove_list_of_users_from_team.assert_called()
        self.mock_slack_service.send_message_to_plaintext_channel_name.assert_not_called()

    @patch("bin.report_on_inactive_users.GithubService", new=MagicMock)
    @patch("bin.report_on_inactive_users.SlackService", new=MagicMock)
    @patch("bin.report_on_inactive_users.get_config")
    @patch("bin.report_on_inactive_users.create_report")
    @patch("bin.report_on_inactive_users.get_environment_variables")
    def test_call_main(self, mock_get_environment_variables, mock_create_report, mock_get_config):
        mock_get_config.return_value = ["", "", ""]
        mock_get_environment_variables.return_value = ["", ""]
        report_test.main()
        mock_get_config.assert_called()
        mock_get_environment_variables.assert_called()
        mock_create_report.assert_called()


if __name__ == '__main__':
    unittest.main()
