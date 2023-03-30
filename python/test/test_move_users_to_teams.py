import os
import unittest
from unittest.mock import patch

from python.scripts import move_users_to_teams

from python.services.github_service import GithubService
from python.lib.constants import Constants
from python.lib.organisation import Organisation


@patch.dict(os.environ, {"CONFIG_FILE": "test-config.yml"})
@patch.dict(os.environ, {"ORG_NAME": "orgname"})
@patch.dict(os.environ, {"ADMIN_GITHUB_TOKEN": "token"})
@patch.object(Constants, "__new__")
@patch.object(Organisation, "__new__")
@patch.object(GithubService, "__new__")
class TestMoveUsersToTeams(unittest.TestCase):

    def test_main_smoke_test(self, mock1, mock2, mock3):
        move_users_to_teams.main()


if __name__ == "__main__":
    unittest.main()
