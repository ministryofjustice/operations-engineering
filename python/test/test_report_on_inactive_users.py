import os
import unittest
from unittest.mock import Mock, patch

import python.scripts.report_on_inactive_users as report_test


class TestReportOnInactiveUsers(unittest.TestCase):
    def setUp(self) -> None:
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

    def test_craft_message_to_users(self):
        user1 = Mock()
        user1.login = "user1"

        user2 = Mock()
        user2.login = "user2"

        users = [user1, user2]
        remove = True
        team_name = "team1"
        inactivity_months = 1

        message = report_test._message_to_users(
            users, remove, team_name, inactivity_months)

        self.assertIn("user1", message)
        self.assertIn("1 months", message)
        self.assertIn("team1", message)

    def test_craft_message_to_users_no_users(self):
        users = []
        remove = True
        team_name = "team1"
        inactivity_months = 1

        message = report_test._message_to_users(
            users, remove, team_name, inactivity_months)

        self.assertEqual(message, "")

    def test_load_team_config(self):
        team = report_test._load_team_config(self.config)

        self.assertEqual('github_team', team.github_team)
        self.assertEqual(True, team.remove_users)
        self.assertEqual('slack_channel', team.slack_channel)


if __name__ == '__main__':
    unittest.main()
