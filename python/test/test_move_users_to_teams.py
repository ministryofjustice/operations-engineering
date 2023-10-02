import os
import unittest
from unittest.mock import patch

from python.scripts import move_users_to_teams
from python.services.github_service import GithubService
from python.lib.organisation import Organisation

# Refactor Status: Done
# Test not needed


@patch.dict(os.environ, {"ORG_NAME": "orgname"})
@patch.dict(os.environ, {"ADMIN_GITHUB_TOKEN": "token"})
@patch.object(Organisation, "__new__")
@patch.object(GithubService, "__new__")
class TestMoveUsersToTeams1(unittest.TestCase):

    def test_main_smoke_test(self, mock1, mock2):
        move_users_to_teams.main()

# Refactor Status: Done
# Test not needed


@patch.dict(os.environ, {"ADMIN_GITHUB_TOKEN": "token"})
@patch.object(Organisation, "__new__")
@patch.object(GithubService, "__new__")
class TestMoveUsersToTeams2(unittest.TestCase):

    def test_detect_org_name_env_var_missing(self, mock1, mock2):
        self.assertRaises(
            ValueError, move_users_to_teams.main)

# Refactor Status: Done
# Test not needed


@patch.dict(os.environ, {"ORG_NAME": "orgname"})
@patch.object(Organisation, "__new__")
@patch.object(GithubService, "__new__")
class TestMoveUsersToTeams3(unittest.TestCase):
    def test_detect_auth_token_env_var_missing(self, mock1, mock2):
        self.assertRaises(
            ValueError, move_users_to_teams.main)


if __name__ == "__main__":
    unittest.main()
