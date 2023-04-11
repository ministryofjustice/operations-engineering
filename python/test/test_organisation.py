import os
import unittest
from unittest.mock import MagicMock, patch

from python.services.github_service import GithubService
from python.lib.organisation import Organisation


@patch.dict(os.environ, {"CONFIG_FILE": "test-config.yml"})
@patch.dict(os.environ, {"ORG_NAME": "orgname"})
@patch.dict(os.environ, {"ADMIN_GITHUB_TOKEN": "token"})
class TestOrganisation(unittest.TestCase):

    def test_create_object(self):
        mock_github_service = MagicMock(GithubService)

        mock_github_service.get_outside_collaborators_login_names.return_value = [
            "collaborator1",
            "collaborator2",
            "collaborator3",
        ]

        mock_github_service.get_team_id_from_team_name.return_value = 1234

        mock_github_service.get_user_permission_for_repository.return_value = "admin"

        mock_github_service.team_exists.return_value = False

        org = Organisation(mock_github_service, "some-org")
        org.setup()
        org.move_direct_users_to_teams()


if __name__ == "__main__":
    unittest.main()
