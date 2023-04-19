import os
import unittest
from unittest.mock import patch

from python.scripts import close_move_users_to_teams_expired_issues
from python.services.github_service import GithubService
from python.lib.organisation import Organisation


@patch.dict(os.environ, {"ADMIN_GITHUB_TOKEN": "token"})
@patch.object(Organisation, "__new__")
@patch.object(GithubService, "__new__")
class TestCloseMoveUsersToTeamsExpiredIssues1(unittest.TestCase):

    def test_main_smoke_test(self, mock1, mock2):
        close_move_users_to_teams_expired_issues.main()


@patch.dict(os.environ, {"WRONG_TOKEN": "token"})
@patch.object(Organisation, "__new__")
@patch.object(GithubService, "__new__")
class TestCloseMoveUsersToTeamsExpiredIssues2(unittest.TestCase):

    def test_detect_env_var_missing(self, mock1, mock2):
        self.assertRaises(
            ValueError, close_move_users_to_teams_expired_issues.main)


if __name__ == "__main__":
    unittest.main()
