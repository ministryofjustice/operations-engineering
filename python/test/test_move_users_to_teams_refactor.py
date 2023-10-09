import os
import unittest
from unittest.mock import patch, MagicMock
import github.Team

from python.config.constants import (
    MINISTRY_OF_JUSTICE,
    MOJ_ANALYTICAL_SERVICES
)


from python.scripts.move_users_to_teams_refactor import (
    main,
    get_ignore_repositories_list,
    get_ignore_teams_list,
    move_remaining_repository_users_into_teams,
    get_environment_variables,
    get_repositories_with_direct_users,
    get_repository_teams,
    raise_issue_on_repository,
    form_team_name,
    get_org_repositories,
    is_new_team_needed,
    create_a_team_on_github,
    get_repository_org_users,
    get_repository_users,
    does_user_have_team_access,
    remove_repository_users_with_team_access,
    ensure_repository_teams_exists,
    put_users_into_repository_teams,
    remove_operations_engineering_team_users_from_team,
    IGNORE_REPOSITORIES_AS_ORG,
    IGNORE_TEAMS_AS_ORG,
    IGNORE_REPOSITORIES_MOJ_ORG,
    IGNORE_TEAMS_MOJ_ORG,
    Repository,
    RepositoryTeam
)


@patch("python.scripts.move_users_to_teams_refactor.get_environment_variables")
@patch("python.scripts.move_users_to_teams_refactor.get_repositories_with_direct_users")
@patch("python.scripts.move_users_to_teams_refactor.remove_repository_users_with_team_access")
@patch("python.scripts.move_users_to_teams_refactor.move_remaining_repository_users_into_teams")
@patch("python.scripts.move_users_to_teams_refactor.GithubService")
class TestMoveUsersToTeamsMain(unittest.TestCase):
    def test_main(self, mock_github_service, mock_move_remaining_repository_users_into_teams, mock_remove_repository_users_with_team_access, mock_get_repositories_with_direct_users, mock_get_environment_variables):
        mock_get_environment_variables.return_value = "", ""
        mock_github_service.get_outside_collaborators_login_names.return_value = []
        main()
        mock_get_repositories_with_direct_users.assert_called()
        mock_get_environment_variables.assert_called()
        mock_remove_repository_users_with_team_access.assert_called()
        mock_move_remaining_repository_users_into_teams.assert_called()


@patch("python.scripts.move_users_to_teams_refactor.get_repository_teams")
@patch("python.scripts.move_users_to_teams_refactor.get_repository_org_users")
@patch("python.scripts.move_users_to_teams_refactor.get_org_repositories")
@patch("python.services.github_service.GithubService")
class TestGeRepositoriesWithDirectUsers(unittest.TestCase):
    def setUp(self):
        self.user = "some-user"
        self.repo_name = "some-repo"
        self.repo = {"name": self.repo_name, "hasIssuesEnabled": True}
        self.team = "some-team"

    def test_get_repositories_with_direct_users_when_users_exist(self, mock_github_service, mock_get_org_repositories, mock_get_repository_org_users, mock_get_repository_teams):
        mock_get_org_repositories.return_value = [self.repo]
        mock_get_repository_org_users.return_value = [self.user]
        mock_get_repository_teams.return_value = [self.team]
        repos = get_repositories_with_direct_users(mock_github_service, [])
        self.assertEqual(len(repos), 1)

    def test_get_repositories_with_direct_users_when_no_org_repos(self, mock_github_service, mock_get_org_repositories, mock_get_repository_org_users, mock_get_repository_teams):
        mock_get_org_repositories.return_value = []
        repos = get_repositories_with_direct_users(mock_github_service, [])
        self.assertEqual(len(repos), 0)

    def test_get_repositories_with_direct_users_when_repo_has_no_users(self, mock_github_service, mock_get_org_repositories, mock_get_repository_org_users, mock_get_repository_teams):
        mock_get_org_repositories.return_value = [self.repo]
        mock_get_repository_org_users.return_value = []
        repos = get_repositories_with_direct_users(mock_github_service, [])
        self.assertEqual(len(repos), 0)

    def test_get_repositories_with_direct_users_when_repo_has_no_teams(self, mock_github_service, mock_get_org_repositories, mock_get_repository_org_users, mock_get_repository_teams):
        mock_get_org_repositories.return_value = [self.repo]
        mock_get_repository_org_users.return_value = [self.user]
        mock_get_repository_teams.return_value = []
        repos = get_repositories_with_direct_users(mock_github_service, [])
        self.assertEqual(len(repos), 1)


class TestMoveUsersToTeamsFunctions(unittest.TestCase):
    def setUp(self):
        self.repo_name = "some-repo"
        self.repository_dict_data = {
            "name": self.repo_name, "collaborators": {"totalCount": 1}, "hasIssuesEnabled": True}
        self.org_outside_collaborators = []
        self.test_user = "some-user"
        self.user = "some-user"
        self.org_name = "some-org"
        self.admin_access = "admin"
        self.team_name = "some-team"
        self.team = RepositoryTeam(
            self.team_name, [self.test_user], self.admin_access, 1)
        self.repository = Repository(self.repo_name, True, [
                                     self.user], [self.team])
        self.admin_team_name = f"{self.repo_name}-{self.admin_access}-team"

    @patch("python.services.github_service.GithubService")
    @patch("python.scripts.move_users_to_teams_refactor.does_user_have_team_access")
    @patch("python.scripts.move_users_to_teams_refactor.raise_issue_on_repository")
    def test_remove_repository_users_with_team_access(self, mock_raise_issue_on_repository, mock_does_user_have_team_access, mock_github_service):
        mock_does_user_have_team_access.return_value = True
        remove_repository_users_with_team_access(
            mock_github_service, [self.repository])
        mock_raise_issue_on_repository.assert_called()
        mock_github_service.remove_user_from_repository.assert_called()

    @patch("python.services.github_service.GithubService")
    @patch("python.scripts.move_users_to_teams_refactor.raise_issue_on_repository")
    def test_remove_repository_users_with_team_access_when_no_repos(self, mock_raise_issue_on_repository, mock_github_service):
        remove_repository_users_with_team_access(mock_github_service, [])
        mock_raise_issue_on_repository.assert_not_called()
        mock_github_service.remove_user_from_repository.assert_not_called()

    @patch("python.services.github_service.GithubService")
    @patch("python.scripts.move_users_to_teams_refactor.raise_issue_on_repository")
    def test_remove_repository_users_with_team_access_when_no_repo_users(self, mock_raise_issue_on_repository, mock_github_service):
        self.repository.direct_users = []
        remove_repository_users_with_team_access(
            mock_github_service, [self.repository])
        mock_raise_issue_on_repository.assert_not_called()
        mock_github_service.remove_user_from_repository.assert_not_called()

    @patch("python.services.github_service.GithubService")
    @patch("python.scripts.move_users_to_teams_refactor.does_user_have_team_access")
    @patch("python.scripts.move_users_to_teams_refactor.raise_issue_on_repository")
    def test_remove_repository_users_with_team_access_when_repo_user_doesnt_have_access(self, mock_raise_issue_on_repository, mock_does_user_have_team_access, mock_github_service):
        mock_does_user_have_team_access.return_value = False
        remove_repository_users_with_team_access(
            mock_github_service, [self.repository])
        mock_raise_issue_on_repository.assert_not_called()
        mock_github_service.remove_user_from_repository.assert_not_called()

    @patch("python.scripts.move_users_to_teams_refactor.get_repository_users")
    @patch("python.services.github_service.GithubService")
    def test_get_repository_org_users(self, mock_github_service, mock_get_repository_users):
        mock_get_repository_users.return_value = [self.user]
        users = get_repository_org_users(
            mock_github_service, self.repository_dict_data, self.org_outside_collaborators)
        self.assertEqual(len(users), 1)

    @patch("python.services.github_service.GithubService")
    def test_get_repository_org_users_when_repo_has_no_users(self, mock_github_service):
        self.repository_dict_data["collaborators"]["totalCount"] = 0
        users = get_repository_org_users(
            mock_github_service, self.repository_dict_data, self.org_outside_collaborators)
        self.assertEqual(len(users), 0)

    @patch("python.services.github_service.GithubService")
    def test_does_user_have_team_access_is_false_because_different_repo_permission(self, mock_github_service):
        mock_github_service.get_user_permission_for_repository.return_value = "pull"
        has_access = does_user_have_team_access(
            mock_github_service, self.repository, self.user)
        self.assertFalse(has_access)

    @patch("python.services.github_service.GithubService")
    def test_does_user_have_team_access_is_true(self, mock_github_service):
        mock_github_service.get_user_permission_for_repository.return_value = self.admin_access
        has_access = does_user_have_team_access(
            mock_github_service, self.repository, self.user)
        self.assertTrue(has_access)

    @patch("python.services.github_service.GithubService")
    def test_does_user_have_team_access_is_false_because_no_repo_teams(self, mock_github_service):
        mock_github_service.get_user_permission_for_repository.return_value = self.admin_access
        self.repository.teams = []
        has_access = does_user_have_team_access(
            mock_github_service, self.repository, self.user)
        self.assertFalse(has_access)

    @patch("python.services.github_service.GithubService")
    def test_does_user_have_team_access_is_false_because_user_not_in_repo_team(self, mock_github_service):
        mock_github_service.get_user_permission_for_repository.return_value = self.admin_access
        self.repository.teams = []
        has_access = does_user_have_team_access(
            mock_github_service, self.repository, "random-user")
        self.assertFalse(has_access)

    @patch("python.services.github_service.GithubService")
    def test_get_repository_users(self, mock_github_service):
        mock_github_service.get_repository_direct_users.return_value = [
            self.user]
        users = get_repository_users(
            mock_github_service, self.repo_name, self.org_outside_collaborators)
        self.assertEqual(len(users), 1)

    @patch("python.services.github_service.GithubService")
    def test_get_repository_users_when_no_users(self, mock_github_service):
        mock_github_service.get_repository_direct_users.return_value = []
        users = get_repository_users(
            mock_github_service, self.repo_name, self.org_outside_collaborators)
        self.assertEqual(len(users), 0)

    @patch("python.services.github_service.GithubService")
    def test_get_repository_users_when_user_a_collaborator(self, mock_github_service):
        mock_github_service.get_repository_direct_users.return_value = [
            self.user]
        self.org_outside_collaborators.append(self.user)
        users = get_repository_users(
            mock_github_service, self.repo_name, self.org_outside_collaborators)
        self.assertEqual(len(users), 0)

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
    @patch("python.scripts.move_users_to_teams_refactor.get_ignore_repositories_list")
    def test_get_org_repositories_when_no_repos(self, mock_get_ignore_repositories_list, mock_github_service):
        mock_get_ignore_repositories_list.return_value = []
        mock_github_service.fetch_all_repositories_in_org.return_value = []
        repos = get_org_repositories(mock_github_service)
        self.assertEqual(len(repos), 0)

    @patch("python.services.github_service.GithubService")
    @patch("python.scripts.move_users_to_teams_refactor.get_ignore_repositories_list")
    def test_get_org_repositories_when_repos_exist(self, mock_get_ignore_repositories_list, mock_github_service):
        mock_get_ignore_repositories_list.return_value = []
        mock_github_service.fetch_all_repositories_in_org.return_value = [
            self.repository_dict_data]
        repos = get_org_repositories(mock_github_service)
        self.assertEqual(len(repos), 1)

    @patch("python.services.github_service.GithubService")
    @patch("python.scripts.move_users_to_teams_refactor.get_ignore_repositories_list")
    def test_get_org_repositories_when_repo_is_in_ignore_list(self, mock_get_ignore_repositories_list, mock_github_service):
        mock_get_ignore_repositories_list.return_value = [
            self.repository_dict_data["name"]]
        mock_github_service.fetch_all_repositories_in_org.return_value = [
            self.repository_dict_data]
        repos = get_org_repositories(mock_github_service)
        self.assertEqual(len(repos), 0)

    @patch("python.services.github_service.GithubService")
    @patch("python.scripts.move_users_to_teams_refactor.get_ignore_teams_list")
    def test_get_repository_teams_when_no_teams_exist(self, mock_get_ignore_teams_list, mock_github_service):
        mock_get_ignore_teams_list.return_value = []
        mock_github_service.organisation_name = self.org_name
        mock_github_service.get_repository_teams.return_value = []
        teams = get_repository_teams(mock_github_service, "")
        self.assertEqual(len(teams), 0)

    @patch("python.services.github_service.GithubService")
    @patch("python.scripts.move_users_to_teams_refactor.get_ignore_teams_list")
    def test_get_repository_teams_when_teams_exists(self, mock_get_ignore_teams_list, mock_github_service):
        mock_team = MagicMock(spec=github.Team.Team)
        mock_get_ignore_teams_list.return_value = []
        mock_github_service.get_repository_teams.return_value = [mock_team]
        mock_github_service.organisation_name = self.org_name
        teams = get_repository_teams(mock_github_service, "")
        self.assertEqual(len(teams), 1)

    @patch("python.services.github_service.GithubService")
    @patch("python.scripts.move_users_to_teams_refactor.get_ignore_teams_list")
    def test_get_repository_teams_when_team_is_in_ignore_list(self, mock_get_ignore_teams_list, mock_github_service):
        mock_team = MagicMock(spec=github.Team.Team)
        mock_team.slug = "some-team"
        mock_get_ignore_teams_list.return_value = ["some-team"]
        mock_github_service.organisation_name = self.org_name
        mock_github_service.get_repository_teams.return_value = [mock_team]
        teams = get_repository_teams(mock_github_service, "")
        self.assertEqual(len(teams), 0)

    @patch("python.scripts.move_users_to_teams_refactor.form_team_name")
    @patch("python.scripts.move_users_to_teams_refactor.get_repository_teams")
    @patch("python.services.github_service.GithubService")
    def test_put_users_into_repository_teams_as_a_user(self, mock_github_service, mock_get_repository_teams, mock_form_team_name):
        mock_get_repository_teams.return_value = [self.team]
        mock_github_service.get_user_permission_for_repository.return_value = "push"
        mock_form_team_name.return_value = self.team_name
        put_users_into_repository_teams(
            mock_github_service, [self.user], self.repo_name)
        mock_github_service.add_user_to_team.assert_called()

    @patch("python.scripts.move_users_to_teams_refactor.form_team_name")
    @patch("python.scripts.move_users_to_teams_refactor.get_repository_teams")
    @patch("python.services.github_service.GithubService")
    def test_put_users_into_repository_teams_as_a_maintainer_as_user_an_admin(self, mock_github_service, mock_get_repository_teams, mock_form_team_name):
        mock_get_repository_teams.return_value = [self.team]
        mock_github_service.get_user_permission_for_repository.return_value = self.admin_access
        mock_form_team_name.return_value = self.team_name
        put_users_into_repository_teams(
            mock_github_service, [self.user], self.repo_name)
        mock_github_service.add_user_to_team_as_maintainer.assert_called()

    @patch("python.scripts.move_users_to_teams_refactor.form_team_name")
    @patch("python.scripts.move_users_to_teams_refactor.get_repository_teams")
    @patch("python.services.github_service.GithubService")
    def test_put_users_into_repository_teams_as_a_maintainer_as_team_empty(self, mock_github_service, mock_get_repository_teams, mock_form_team_name):
        self.team.users = []
        mock_get_repository_teams.return_value = [self.team]
        mock_github_service.get_user_permission_for_repository.return_value = self.admin_access
        mock_form_team_name.return_value = self.team_name
        put_users_into_repository_teams(
            mock_github_service, [self.user], self.repo_name)
        mock_github_service.add_user_to_team_as_maintainer.assert_called()

    @patch("python.scripts.move_users_to_teams_refactor.form_team_name")
    @patch("python.scripts.move_users_to_teams_refactor.get_repository_teams")
    @patch("python.services.github_service.GithubService")
    def test_put_users_into_repository_teams_doesnt_as_repo_team_names_dont_match(self, mock_github_service, mock_get_repository_teams, mock_form_team_name):
        mock_get_repository_teams.return_value = [self.team]
        mock_github_service.get_user_permission_for_repository.return_value = self.admin_access
        mock_form_team_name.return_value = "random-team"
        put_users_into_repository_teams(
            mock_github_service, [self.user], self.repo_name)
        mock_github_service.add_user_to_team.assert_not_called()
        mock_github_service.add_user_to_team_as_maintainer.assert_not_called()

    @patch("python.scripts.move_users_to_teams_refactor.form_team_name")
    @patch("python.scripts.move_users_to_teams_refactor.get_repository_teams")
    @patch("python.services.github_service.GithubService")
    def test_put_users_into_repository_teams_doesnt_as_no_repo_teams(self, mock_github_service, mock_get_repository_teams, mock_form_team_name):
        mock_get_repository_teams.return_value = []
        mock_github_service.get_user_permission_for_repository.return_value = self.admin_access
        mock_form_team_name.return_value = self.team_name
        put_users_into_repository_teams(
            mock_github_service, [self.user], self.repo_name)
        mock_github_service.add_user_to_team.assert_not_called()
        mock_github_service.add_user_to_team_as_maintainer.assert_not_called()

    @patch("python.scripts.move_users_to_teams_refactor.get_repository_teams")
    @patch("python.services.github_service.GithubService")
    def test_put_users_into_repository_teams_doesnt_as_no_users(self, mock_github_service, mock_get_repository_teams):
        mock_get_repository_teams.return_value = []
        put_users_into_repository_teams(
            mock_github_service, [self.user], self.repo_name)
        mock_github_service.add_user_to_team.assert_not_called()
        mock_github_service.add_user_to_team_as_maintainer.assert_not_called()

    def test_form_correct_team_name_combinations(self):
        self.assertEqual(form_team_name(self.admin_access,
                         self.repo_name), self.admin_team_name)
        self.assertEqual(form_team_name(
            "write", self.repo_name), "some-repo-write-team")
        self.assertEqual(form_team_name(
            "read", self.repo_name), "some-repo-read-team")
        self.assertEqual(form_team_name(
            "maintain", self.repo_name), "some-repo-maintain-team")

    def test_fix_incorrect_team_name_combinations(self):
        repo_name = ".some-repo"
        self.assertEqual(form_team_name(self.admin_access,
                         repo_name), self.admin_team_name)

        repo_name = ".some-repo."
        self.assertEqual(form_team_name(self.admin_access,
                         repo_name), self.admin_team_name)

        repo_name = "some-repo."
        self.assertEqual(form_team_name(self.admin_access,
                         repo_name), self.admin_team_name)

        repo_name = "-some-repo"
        self.assertEqual(form_team_name(self.admin_access,
                         repo_name), self.admin_team_name)

        repo_name = "-some-repo-"
        self.assertEqual(form_team_name(self.admin_access,
                         repo_name), self.admin_team_name)

        repo_name = "some-repo-"
        self.assertEqual(form_team_name(self.admin_access,
                         repo_name), self.admin_team_name)

        repo_name = "--some-repo"
        self.assertEqual(form_team_name(self.admin_access,
                         repo_name), self.admin_team_name)

        repo_name = "--some-repo--"
        self.assertEqual(form_team_name(self.admin_access,
                         repo_name), self.admin_team_name)

        repo_name = "--some--repo--"
        self.assertEqual(form_team_name(self.admin_access,
                         repo_name), self.admin_team_name)

        repo_name = "---some---repo---"
        self.assertEqual(form_team_name(self.admin_access,
                         repo_name), self.admin_team_name)

        repo_name = "---.some-.--repo---."
        self.assertEqual(form_team_name(self.admin_access,
                         repo_name), self.admin_team_name)

        repo_name = "-_-.some-.--repo-_-."
        self.assertEqual(form_team_name(self.admin_access,
                         repo_name), self.admin_team_name)

        repo_name = "_some_repo_"
        self.assertEqual(form_team_name(self.admin_access,
                         repo_name), self.admin_team_name)

        repo_name = "some_repo_"
        self.assertEqual(form_team_name(self.admin_access,
                         repo_name), self.admin_team_name)

        repo_name = "_some_repo"
        self.assertEqual(form_team_name(self.admin_access,
                         repo_name), self.admin_team_name)

        repo_name = " some repo "
        self.assertEqual(form_team_name(self.admin_access,
                         repo_name), self.admin_team_name)

        repo_name = " some-repo"
        self.assertEqual(form_team_name(self.admin_access,
                         repo_name), self.admin_team_name)

        repo_name = "some repo"
        self.assertEqual(form_team_name(self.admin_access,
                         repo_name), self.admin_team_name)

        repo_name = "..some-repo.."
        self.assertEqual(form_team_name(self.admin_access,
                         repo_name), self.admin_team_name)

    def test_is_new_team_needed_not_needed(self):
        self.assertFalse(is_new_team_needed(self.team_name, [self.team]))

    def test_is_new_team_needed_is_needed(self):
        self.assertTrue(is_new_team_needed("random-team", [self.team]))

    def test_is_new_team_needed_when_no_team_in_list(self):
        self.assertTrue(is_new_team_needed(self.team_name, []))

    @patch("python.services.github_service.GithubService")
    def test_create_a_team_on_github(self, mock_github_service):
        mock_github_service.team_exists.return_value = False
        mock_github_service.get_team_id_from_team_name.return_value = 123
        team_id = create_a_team_on_github(
            mock_github_service, self.team_name, self.repo_name)
        mock_github_service.create_new_team_with_repository.assert_called()
        mock_github_service.get_team_id_from_team_name.assert_called()
        self.assertEqual(team_id, 123)

    @patch("python.services.github_service.GithubService")
    def test_create_a_team_on_github_doesnt(self, mock_github_service):
        mock_github_service.team_exists.return_value = True
        team_id = create_a_team_on_github(
            mock_github_service, self.team_name, self.repo_name)
        mock_github_service.create_new_team_with_repository.assert_not_called()
        mock_github_service.get_team_id_from_team_name.assert_not_called()
        self.assertEqual(team_id, 0)

    @patch("python.services.github_service.GithubService")
    def test_remove_operations_engineering_team_users_from_team(self, mock_github_service):
        mock_github_service.get_a_team_usernames.return_value = [self.user]
        remove_operations_engineering_team_users_from_team(
            mock_github_service, 123)
        mock_github_service.remove_user_from_team.assert_called()

    @patch("python.services.github_service.GithubService")
    def test_remove_operations_engineering_team_users_from_team_isnt_called(self, mock_github_service):
        mock_github_service.get_a_team_usernames.return_value = []
        remove_operations_engineering_team_users_from_team(
            mock_github_service, 123)
        mock_github_service.remove_user_from_team.assert_not_called()

    @patch("python.scripts.move_users_to_teams_refactor.remove_operations_engineering_team_users_from_team")
    @patch("python.scripts.move_users_to_teams_refactor.create_a_team_on_github")
    @patch("python.scripts.move_users_to_teams_refactor.is_new_team_needed")
    @patch("python.scripts.move_users_to_teams_refactor.form_team_name")
    @patch("python.services.github_service.GithubService")
    def test_ensure_repository_teams_exists(self, mock_github_service, mock_form_team_name, mock_is_new_team_needed, mock_create_a_team_on_github, mock_remove_operations_engineering_team_users_from_team):
        mock_github_service.get_user_permission_for_repository.return_value = self.admin_access
        mock_form_team_name.return_value = "team"
        mock_create_a_team_on_github.return_value = 123
        mock_is_new_team_needed.return_value = True
        ensure_repository_teams_exists(
            mock_github_service, [self.user], self.repo_name, [self.team])
        mock_github_service.amend_team_permissions_for_repository.assert_called()
        mock_remove_operations_engineering_team_users_from_team.assert_called()

    @patch("python.scripts.move_users_to_teams_refactor.remove_operations_engineering_team_users_from_team")
    @patch("python.scripts.move_users_to_teams_refactor.create_a_team_on_github")
    @patch("python.scripts.move_users_to_teams_refactor.is_new_team_needed")
    @patch("python.scripts.move_users_to_teams_refactor.form_team_name")
    @patch("python.services.github_service.GithubService")
    def test_ensure_repository_teams_exists_when_no_team_created_on_gh(self, mock_github_service, mock_form_team_name, mock_is_new_team_needed, mock_create_a_team_on_github, mock_remove_operations_engineering_team_users_from_team):
        mock_github_service.get_user_permission_for_repository.return_value = self.admin_access
        mock_form_team_name.return_value = "team"
        mock_create_a_team_on_github.return_value = 0
        mock_is_new_team_needed.return_value = True
        ensure_repository_teams_exists(
            mock_github_service, [self.user], self.repo_name, [self.team])
        mock_github_service.amend_team_permissions_for_repository.assert_not_called()
        mock_remove_operations_engineering_team_users_from_team.assert_not_called()

    @patch("python.scripts.move_users_to_teams_refactor.create_a_team_on_github")
    @patch("python.scripts.move_users_to_teams_refactor.is_new_team_needed")
    @patch("python.scripts.move_users_to_teams_refactor.form_team_name")
    @patch("python.services.github_service.GithubService")
    def test_ensure_repository_teams_exists_when_no_new_team_is_needed(self, mock_github_service, mock_form_team_name, mock_is_new_team_needed, mock_create_a_team_on_github):
        mock_github_service.get_user_permission_for_repository.return_value = self.admin_access
        mock_form_team_name.return_value = "team"
        mock_is_new_team_needed.return_value = False
        ensure_repository_teams_exists(
            mock_github_service, [self.user], self.repo_name, [self.team])
        mock_create_a_team_on_github.assert_not_called()

    @patch("python.scripts.move_users_to_teams_refactor.form_team_name")
    @patch("python.services.github_service.GithubService")
    def test_ensure_repository_teams_exists_when_no_users(self, mock_github_service, mock_form_team_name):
        ensure_repository_teams_exists(
            mock_github_service, [], self.repo_name, [self.team])
        mock_github_service.get_user_permission_for_repository.assert_not_called()
        mock_form_team_name.assert_not_called()

    @patch("python.services.github_service.GithubService")
    def test_raise_issue_on_repository(self, mock_github_service):
        raise_issue_on_repository(
            mock_github_service, self.repo_name, True, self.user)
        mock_github_service.create_an_access_removed_issue_for_user_in_repository.assert_called()

    @patch("python.services.github_service.GithubService")
    def test_raise_issue_on_repository_doesnt(self, mock_github_service):
        raise_issue_on_repository(
            mock_github_service, self.repo_name, False, self.user)
        mock_github_service.create_an_access_removed_issue_for_user_in_repository.assert_not_called()

    @patch("python.scripts.move_users_to_teams_refactor.raise_issue_on_repository")
    @patch("python.scripts.move_users_to_teams_refactor.put_users_into_repository_teams")
    @patch("python.scripts.move_users_to_teams_refactor.ensure_repository_teams_exists")
    @patch("python.scripts.move_users_to_teams_refactor.get_repository_users")
    @patch("python.services.github_service.GithubService")
    def test_move_remaining_repository_users_into_teams(self, mock_github_service, mock_get_repository_users, mock_ensure_repository_teams_exists, mock_put_users_into_repository_teams, mock_raise_issue_on_repository):
        mock_get_repository_users.return_value = [self.user]
        move_remaining_repository_users_into_teams(
            mock_github_service, [self.repository], self.org_outside_collaborators)
        mock_ensure_repository_teams_exists.assert_called()
        mock_github_service.remove_user_from_repository.assert_called()
        mock_put_users_into_repository_teams.assert_called()
        mock_raise_issue_on_repository.assert_called()

    @patch("python.scripts.move_users_to_teams_refactor.raise_issue_on_repository")
    @patch("python.scripts.move_users_to_teams_refactor.put_users_into_repository_teams")
    @patch("python.scripts.move_users_to_teams_refactor.ensure_repository_teams_exists")
    @patch("python.scripts.move_users_to_teams_refactor.get_repository_users")
    @patch("python.services.github_service.GithubService")
    def test_move_remaining_repository_users_into_teams_when_no_users(self, mock_github_service, mock_get_repository_users, mock_ensure_repository_teams_exists, mock_put_users_into_repository_teams, mock_raise_issue_on_repository):
        mock_get_repository_users.return_value = []
        move_remaining_repository_users_into_teams(
            mock_github_service, [self.repository], self.org_outside_collaborators)
        mock_ensure_repository_teams_exists.assert_not_called()
        mock_github_service.remove_user_from_repository.assert_not_called()
        mock_put_users_into_repository_teams.assert_not_called()
        mock_raise_issue_on_repository.assert_not_called()


if __name__ == "__main__":
    unittest.main()
