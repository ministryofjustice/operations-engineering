import os
import unittest
import github.Team
from unittest.mock import patch, MagicMock

from python.services.github_service import GithubService

from python.config.constants import (
    MINISTRY_OF_JUSTICE,
    MOJ_ANALYTICAL_SERVICES
)


from python.scripts.move_users_to_teams_refactor import (
    main,
    get_ignore_repositories_list,
    get_ignore_teams_list,
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
        self.repository_data = {
            "name": "some-repo", "collaborators": {"totalCount": 1}, "hasIssuesEnabled": True}
        self.org_outside_collaborators = []
        self.test_user = "some-user"

    def test_get_ignore_teams_list_moj_org(self):
        ignore_teams = get_ignore_teams_list(MINISTRY_OF_JUSTICE)
        self.assertEqual(ignore_teams, IGNORE_TEAMS_MOJ_ORG)

    def test_get_ignore_teams_list_as_org(self):
        ignore_teams = get_ignore_teams_list(MOJ_ANALYTICAL_SERVICES)
        self.assertEqual(ignore_teams, IGNORE_TEAMS_AS_ORG)

    def test_get_ignore_repositories_list_as_org(self):
        ignore_repositories = get_ignore_repositories_list(
            MOJ_ANALYTICAL_SERVICES)
        self.assertEqual(ignore_repositories, IGNORE_REPOSITORIES_AS_ORG)

    def test_get_ignore_repositories_list_moj_org(self):
        ignore_repositories = get_ignore_repositories_list(MINISTRY_OF_JUSTICE)
        self.assertEqual(ignore_repositories, IGNORE_REPOSITORIES_MOJ_ORG)

    def test_get_ignore_teams_list_raises_exception(self):
        self.assertRaises(
            ValueError, get_ignore_teams_list, "some-org")

    def test_get_ignore_repositories_list_raises_exception(self):
        self.assertRaises(
            ValueError, get_ignore_repositories_list, "some-org")

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
        mock_github_service.get_repository_direct_users.return_value = [
            self.test_user]
        users = get_repo_direct_access_users(
            mock_github_service, self.repository_data, self.org_outside_collaborators)
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0], self.test_user)

    @patch("python.services.github_service.GithubService")
    def test_get_repo_direct_access_users_when_no_exist(self, mock_github_service):
        mock_github_service.get_repository_direct_users.return_value = []
        users = get_repo_direct_access_users(
            mock_github_service, self.repository_data, self.org_outside_collaborators)
        self.assertEqual(len(users), 0)

    @patch("python.services.github_service.GithubService")
    def test_get_repo_direct_access_users_when_repo_has_no_direct_users(self, mock_github_service):
        self.repository_data["collaborators"]["totalCount"] = 0
        users = get_repo_direct_access_users(
            mock_github_service, self.repository_data, self.org_outside_collaborators)
        self.assertEqual(len(users), 0)

    @patch("python.services.github_service.GithubService")
    def test_get_repo_direct_access_users_excludes_collaborator(self, mock_github_service):
        self.repository_data["collaborators"]["totalCount"] = 2
        self.org_outside_collaborators.append("collaborator")
        mock_github_service.get_repository_direct_users.return_value = [
            "collaborator", self.test_user]
        users = get_repo_direct_access_users(
            mock_github_service, self.repository_data, self.org_outside_collaborators)
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0], self.test_user)

    @patch("python.services.github_service.GithubService")
    def test_get_ops_eng_team_usernames(self, mock_github_service):
        mock_github_service.get_a_team_usernames.return_value = [
            self.test_user, self.test_user]
        users = get_ops_eng_team_usernames(mock_github_service)
        self.assertEqual(len(users), 2)
        self.assertEqual(users, [self.test_user, self.test_user])

    @patch("python.scripts.move_users_to_teams_refactor.get_org_repositories")
    @patch("python.services.github_service.GithubService")
    def test_get_repositories_with_direct_users_when_no_org_repos(self, mock_github_service, mock_get_org_repositories):
        mock_get_org_repositories.return_value = []
        repos = get_repositories_with_direct_users(mock_github_service, "")
        self.assertEqual(len(repos), 0)

    @patch("python.scripts.move_users_to_teams_refactor.get_repo_direct_access_users")
    @patch("python.scripts.move_users_to_teams_refactor.get_org_repositories")
    @patch("python.services.github_service.GithubService")
    def test_get_repositories_with_direct_users_when_no_direct_repo_users(self, mock_github_service, mock_get_org_repositories, mock_get_repo_direct_access_users):
        mock_get_org_repositories.return_value = [self.repository_data]
        mock_get_repo_direct_access_users.return_value = []
        repos = get_repositories_with_direct_users(mock_github_service, "")
        self.assertEqual(len(repos), 0)

    @patch("python.scripts.move_users_to_teams_refactor.get_repository_teams")
    @patch("python.scripts.move_users_to_teams_refactor.get_repo_direct_access_users")
    @patch("python.scripts.move_users_to_teams_refactor.get_org_repositories")
    @patch("python.services.github_service.GithubService")
    def test_get_repositories_with_direct_users_when_repo_has_direct_users(self, mock_github_service, mock_get_org_repositories, mock_get_repo_direct_access_users, mock_get_repository_teams):
        mock_get_org_repositories.return_value = [self.repository_data]
        mock_get_repo_direct_access_users.return_value = [self.test_user]
        mock_get_repository_teams.return_value = []
        repos = get_repositories_with_direct_users(mock_github_service, "")
        self.assertEqual(len(repos), 1)

    @patch("python.services.github_service.GithubService")
    @patch("python.scripts.move_users_to_teams_refactor.get_ignore_repositories_list")
    def test_get_org_repositories_when_no_repos(self, mock_get_ignore_repositories_list, mock_github_service):
        mock_get_ignore_repositories_list.return_value = []
        mock_github_service.fetch_all_repositories_in_org.return_value = []
        repos = get_org_repositories(mock_github_service, "")
        self.assertEqual(len(repos), 0)

    @patch("python.services.github_service.GithubService")
    @patch("python.scripts.move_users_to_teams_refactor.get_ignore_repositories_list")
    def test_get_org_repositories_when_repos_exist(self, mock_get_ignore_repositories_list, mock_github_service):
        mock_get_ignore_repositories_list.return_value = []
        mock_github_service.fetch_all_repositories_in_org.return_value = [
            {"node": self.repository_data}]
        repos = get_org_repositories(mock_github_service, "")
        self.assertEqual(len(repos), 1)

    @patch("python.services.github_service.GithubService")
    @patch("python.scripts.move_users_to_teams_refactor.get_ignore_repositories_list")
    def test_get_org_repositories_when_repo_is_in_ignore_list(self, mock_get_ignore_repositories_list, mock_github_service):
        mock_get_ignore_repositories_list.return_value = [
            self.repository_data["name"]]
        mock_github_service.fetch_all_repositories_in_org.return_value = [
            {"node": self.repository_data}]
        repos = get_org_repositories(mock_github_service, "")
        self.assertEqual(len(repos), 0)

    @patch("python.services.github_service.GithubService")
    @patch("python.scripts.move_users_to_teams_refactor.get_ignore_teams_list")
    def test_get_repository_teams_when_no_teams_exist(self, mock_get_ignore_teams_list, mock_github_service):
        mock_get_ignore_teams_list.return_value = []
        mock_github_service.get_repository_teams.return_value = []
        teams = get_repository_teams(mock_github_service, "", "")
        self.assertEqual(len(teams), 0)

    @patch("python.services.github_service.GithubService")
    @patch("python.scripts.move_users_to_teams_refactor.get_ignore_teams_list")
    def test_get_repository_teams_when_teams_exists(self, mock_get_ignore_teams_list, mock_github_service):
        mock_team = MagicMock(spec=github.Team.Team)
        mock_get_ignore_teams_list.return_value = []
        mock_github_service.get_repository_teams.return_value = [mock_team]
        teams = get_repository_teams(mock_github_service, "", "")
        self.assertEqual(len(teams), 1)

    @patch("python.services.github_service.GithubService")
    @patch("python.scripts.move_users_to_teams_refactor.get_ignore_teams_list")
    def test_get_repository_teams_when_team_is_in_ignore_list(self, mock_get_ignore_teams_list, mock_github_service):
        mock_team = MagicMock(spec=github.Team.Team)
        mock_team.name = "some-team"
        mock_get_ignore_teams_list.return_value = ["some-team"]
        mock_github_service.get_repository_teams.return_value = [mock_team]
        teams = get_repository_teams(mock_github_service, "", "")
        self.assertEqual(len(teams), 0)


if __name__ == "__main__":
    unittest.main()
