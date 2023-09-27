import os
import unittest
from unittest.mock import patch, MagicMock

from python.services.github_service import GithubService

from python.config.constants import (
    MINISTRY_OF_JUSTICE,
    MOJ_ANALYTICAL_SERVICES
)


from python.scripts.move_users_to_teams_refactor import (
    main,
    get_ignore_lists,
    get_environment_variables,
    get_repo_direct_access_users,
    get_ops_eng_team_usernames,
    get_repository_teams,
    get_org_repositories,
    get_repositories_with_direct_users,
    IGNORE_REPOSITORIES_AS_ORG,
    IGNORE_TEAMS_AS_ORG,
    IGNORE_REPOSITORIES_MOJ_ORG,
    IGNORE_TEAMS_MOJ_ORG
)

@patch("python.scripts.move_users_to_teams_refactor.GithubService", new=MagicMock)
@patch("python.scripts.move_users_to_teams_refactor.get_environment_variables")
@patch("python.scripts.move_users_to_teams_refactor.get_ops_eng_team_usernames")
@patch("python.scripts.move_users_to_teams_refactor.get_repositories_with_direct_users")
class TestMoveUsersToTeamsMain(unittest.TestCase):
    def test_main(self, mock_get_repositories_with_direct_users, mock_get_ops_eng_team_usernames, mock_get_environment_variables):
        mock_get_environment_variables.return_value = "", ""
        mock_get_ops_eng_team_usernames.return_value = MagicMock()
        mock_get_repositories_with_direct_users.return_value = MagicMock()
        main()
        mock_get_repositories_with_direct_users.assert_called()
        mock_get_ops_eng_team_usernames.assert_called()
        mock_get_environment_variables.assert_called()


class TestMoveUsersToTeams(unittest.TestCase):
    def setUp(self):
        self.repository_data = {"repository_name": "some-repo", "number_of_direct_users": 1, "issue_section_enabled": True}
        self.org_outside_collaborators = []
        self.test_user = "some-user"

    def test_get_ignore_lists(self):
        ignore_repositories, ignore_teams = get_ignore_lists(MINISTRY_OF_JUSTICE)
        self.assertEqual(ignore_repositories, IGNORE_REPOSITORIES_MOJ_ORG)
        self.assertEqual(ignore_teams, IGNORE_TEAMS_MOJ_ORG)

        ignore_repositories, ignore_teams = get_ignore_lists(MOJ_ANALYTICAL_SERVICES)
        self.assertEqual(ignore_repositories, IGNORE_REPOSITORIES_AS_ORG)
        self.assertEqual(ignore_teams, IGNORE_TEAMS_AS_ORG)

    def test_get_allow_list_users_raise_error(self):
        self.assertRaises(
            ValueError, get_ignore_lists, "some-org")

    @patch.dict(os.environ, {"ADMIN_GITHUB_TOKEN": "token", "ORG_NAME": "name"})
    def test_get_environment_variables(self):
        github_token, org_name = get_environment_variables()
        self.assertEqual(github_token, "token")
        self.assertEqual(org_name, "name")

    @patch.dict(os.environ, {"ADMIN_GITHUB_TOKEN": "token"})
    def test_get_environment_variables_when_no_org_name_raises_exception(self):
        self.assertRaises(ValueError, get_environment_variables)

    @patch.dict(os.environ, {"ORG_NAME": "name"})
    def test_get_environment_variables_when_no_gh_token_raises_exception(self):
        self.assertRaises(ValueError, get_environment_variables)

    @patch("python.services.github_service.GithubService")
    def test_get_repo_direct_access_users_when_users_exist(self, mock_github_service):
        mock_github_service.get_repository_direct_users.return_value = [self.test_user]
        users = get_repo_direct_access_users(mock_github_service, self.repository_data, self.org_outside_collaborators)
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0], self.test_user)

    @patch("python.services.github_service.GithubService")
    def test_get_repo_direct_access_users_when_no_exist(self, mock_github_service):
        mock_github_service.get_repository_direct_users.return_value = []
        users = get_repo_direct_access_users(mock_github_service, self.repository_data, self.org_outside_collaborators)
        self.assertEqual(len(users), 0)

    @patch("python.services.github_service.GithubService")
    def test_get_repo_direct_access_users_when_repo_has_no_direct_users(self, mock_github_service):
        self.repository_data["number_of_direct_users"] = 0
        users = get_repo_direct_access_users(mock_github_service, self.repository_data, self.org_outside_collaborators)
        self.assertEqual(len(users), 0)

    @patch("python.services.github_service.GithubService")
    def test_get_repo_direct_access_users_excludes_collaborator(self, mock_github_service):
        self.repository_data["number_of_direct_users"] = 2
        self.org_outside_collaborators.append("collaborator")
        mock_github_service.get_repository_direct_users.return_value = ["collaborator", self.test_user]
        users = get_repo_direct_access_users(mock_github_service, self.repository_data, self.org_outside_collaborators)
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0], self.test_user)

    @patch("python.services.github_service.GithubService")
    def test_get_ops_eng_team_usernames(self, mock_github_service):
        mock_github_service.get_a_team_usernames.return_value = [self.test_user, self.test_user]
        users = get_ops_eng_team_usernames(mock_github_service)
        self.assertEqual(len(users), 2)
        self.assertEqual(users, [self.test_user, self.test_user])

    def test_get_repositories_with_direct_users(self):
        pass

if __name__ == "__main__":
    unittest.main()
