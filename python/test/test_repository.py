import unittest
from unittest.mock import MagicMock, patch, call

from python.services.github_service import GithubService
from python.lib.repository import Repository

# Refactor Status: Done
# Test not needed
class TestRepository1(unittest.TestCase):

    def test_smoke_test(self):
        mock_github_service = MagicMock(GithubService)
        Repository(
            mock_github_service,
            "some-repo",
            True,
            [],
            [],
            []
        )


class TestRepository2(unittest.TestCase):

    # Refactor Status: Done
    # Not needed
    def setUp(self):
        self.mock_github_service = MagicMock(GithubService)
        self.repo = Repository(
            self.mock_github_service,
            "some-repo",
            True,
            [],
            [],
            []
        )

    # Refactor Status: Done
    # Test not needed
    def test_do_not_remove_operations_engineering_team_users_from_team_as_team_empty(self):
        self.repo.remove_operations_engineering_team_users_from_team(12345)
        self.mock_github_service.remove_user_from_team.assert_not_called()

    def test_do_not_create_repo_issues_for_direct_users_when_no_direct_users(self):
        self.repo.create_repo_issues_for_direct_users()
        self.mock_github_service.create_an_access_removed_issue_for_user_in_repository.assert_not_called()

    # Refactor Status: Done
    # Test moved to test_put_users_into_repository_teams_doesnt_as_no_users()
    def test_do_not_put_direct_users_into_teams_when_no_direct_users(self):
        self.repo.put_direct_users_into_teams()
        self.mock_github_service.add_user_to_team_as_maintainer.assert_not_called()
        self.mock_github_service.add_user_to_team.assert_not_called()

    def test_is_new_team_needed_when_no_teams_exist(self):
        self.assertEqual(self.repo.is_new_team_needed(
            "admin"), True)

    @patch("github.Team")
    def test_is_new_team_needed_when_no_matching_teams_exist(self, mock_github_team):
        mock_github_team.name = "some-repo-pull-team"
        self.repo.add_team(mock_github_team)
        self.assertEqual(self.repo.is_new_team_needed(
            "admin"), True)

    @patch("github.Team")
    def test_is_new_team_needed_when_a_matching_teams_exist(self, mock_github_team):
        mock_github_team.name = "some-repo-admin-team"
        self.repo.add_team(mock_github_team)
        self.assertEqual(self.repo.is_new_team_needed(
            "admin"), False)

    def test_dont_make_team_when_no_direct_users(self):
        self.repo.ensure_repository_teams_exists()
        self.assertEqual(len(self.repo.teams), 0)

    # Refactor Status: Done
    # Test moved to test_move_users_to_teams_refactor.py
    def test_form_correct_team_name_combinations(self):
        self.assertEqual(self.repo.form_team_name(
            "admin"), "some-repo-admin-team")

        self.assertEqual(self.repo.form_team_name(
            "write"), "some-repo-write-team")

        self.assertEqual(self.repo.form_team_name(
            "read"), "some-repo-read-team")

        self.assertEqual(self.repo.form_team_name(
            "maintain"), "some-repo-maintain-team")

    # Refactor Status: Done
    # Test moved to test_move_users_to_teams_refactor.py
    def test_fix_incorrect_team_name_combinations(self):
        self.repo.name = ".some-repo"
        self.assertEqual(self.repo.form_team_name(
            "admin"), "some-repo-admin-team")

        self.repo.name = ".some-repo."
        self.assertEqual(self.repo.form_team_name(
            "admin"), "some-repo-admin-team")

        self.repo.name = "some-repo."
        self.assertEqual(self.repo.form_team_name(
            "admin"), "some-repo-admin-team")

        self.repo.name = "-some-repo"
        self.assertEqual(self.repo.form_team_name(
            "admin"), "some-repo-admin-team")

        self.repo.name = "-some-repo-"
        self.assertEqual(self.repo.form_team_name(
            "admin"), "some-repo-admin-team")

        self.repo.name = "some-repo-"
        self.assertEqual(self.repo.form_team_name(
            "admin"), "some-repo-admin-team")

        self.repo.name = "--some-repo"
        self.assertEqual(self.repo.form_team_name(
            "admin"), "some-repo-admin-team")

        self.repo.name = "--some-repo--"
        self.assertEqual(self.repo.form_team_name(
            "admin"), "some-repo-admin-team")

        self.repo.name = "--some--repo--"
        self.assertEqual(self.repo.form_team_name(
            "admin"), "some-repo-admin-team")

        self.repo.name = "---some---repo---"
        self.assertEqual(self.repo.form_team_name(
            "admin"), "some-repo-admin-team")

        self.repo.name = "---.some-.--repo---."
        self.assertEqual(self.repo.form_team_name(
            "admin"), "some-repo-admin-team")

        self.repo.name = "-_-.some-.--repo-_-."
        self.assertEqual(self.repo.form_team_name(
            "admin"), "some-repo-admin-team")

        self.repo.name = "_some_repo_"
        self.assertEqual(self.repo.form_team_name(
            "admin"), "some-repo-admin-team")

        self.repo.name = "some_repo_"
        self.assertEqual(self.repo.form_team_name(
            "admin"), "some-repo-admin-team")

        self.repo.name = "_some_repo"
        self.assertEqual(self.repo.form_team_name(
            "admin"), "some-repo-admin-team")

        self.repo.name = " some repo "
        self.assertEqual(self.repo.form_team_name(
            "admin"), "some-repo-admin-team")

        self.repo.name = " some-repo"
        self.assertEqual(self.repo.form_team_name(
            "admin"), "some-repo-admin-team")

        self.repo.name = "some repo"
        self.assertEqual(self.repo.form_team_name(
            "admin"), "some-repo-admin-team")

        self.repo.name = "..some-repo.."
        self.assertEqual(self.repo.form_team_name(
            "admin"), "some-repo-admin-team")


class TestRepository3(unittest.TestCase):

    # Refactor Status: Done
    # Not needed
    def setUp(self):
        self.mock_github_service = MagicMock(GithubService)
        self.repo = Repository(
            self.mock_github_service,
            "some-repo",
            True,
            [],
            [],
            []
        )

        self.mock_github_service.get_user_permission_for_repository.return_value = "admin"
        self.repo.direct_users = ["user1"]

    # Refactor Status: Done
    # Test moved to test_put_users_into_repository_teams_doesnt_as_no_repo_teams
    def test_do_not_put_direct_users_into_teams_when_no_teams(self):
        self.repo.put_direct_users_into_teams()
        self.mock_github_service.add_user_to_team_as_maintainer.assert_not_called()
        self.mock_github_service.add_user_to_team.assert_not_called()

    # Refactor Status: Done
    # Test not needed
    @patch("github.Team")
    def test_do_not_put_direct_users_into_teams_when_team_permission_doesnt_match(self, mock_github_team):
        mock_github_team.name = "some-repo-pull-team"
        self.repo.add_team(mock_github_team)
        self.repo.put_direct_users_into_teams()
        self.mock_github_service.add_user_to_team_as_maintainer.assert_not_called()
        self.mock_github_service.add_user_to_team.assert_not_called()

    # Refactor Status: Done
    # Test moved to test_put_users_into_repository_teams_as_a_maintainer_as_user_an_admin
    @patch("github.Team")
    def test_put_direct_users_into_admin_teams(self, mock_github_team):
        mock_github_team.name = "some-repo-admin-team"
        self.repo.add_team(mock_github_team)
        self.repo.put_direct_users_into_teams()
        self.mock_github_service.add_user_to_team_as_maintainer.assert_called_once()
        self.mock_github_service.add_user_to_team.assert_not_called()

    @patch("github.Team")
    def test_dont_make_team_when_team_already_exists(self, mock_github_team):
        mock_github_team.name = "some-repo-admin-team"
        self.repo.add_team(mock_github_team)
        self.assertEqual(len(self.repo.teams), 1)
        self.repo.ensure_repository_teams_exists()
        self.assertEqual(len(self.repo.teams), 1)

    @patch("github.Team")
    def test_make_a_team_fails_on_github(self, mock_github_team):
        mock_github_team.name = "some-repo-write-team"
        self.repo.add_team(mock_github_team)
        self.assertEqual(len(self.repo.teams), 1)
        self.repo.ensure_repository_teams_exists()
        self.assertEqual(len(self.repo.teams), 1)

    @patch("github.Team")
    def test_fail_to_make_a_team_on_github_because_team_already_exists(self, mock_github_team):
        mock_github_team.name = "some-repo-write-team"
        self.repo.add_team(mock_github_team)
        self.assertEqual(len(self.repo.teams), 1)
        self.mock_github_service.team_exists.return_value = True
        self.repo.ensure_repository_teams_exists()
        self.assertEqual(len(self.repo.teams), 1)

    @patch("github.Team")
    def test_fail_to_make_a_team_on_github_because_cannot_find_the_team(self, mock_github_team):
        mock_github_team.name = "some-repo-write-team"
        self.repo.add_team(mock_github_team)
        self.assertEqual(len(self.repo.teams), 1)
        self.mock_github_service.team_exists.return_value = False
        self.mock_github_service.get_team_id_from_team_name.return_value = 12345
        mock_github_team.name = "some-repo-read-team"
        self.mock_github_service.get_repository_teams.return_value = [
            mock_github_team]
        self.repo.ensure_repository_teams_exists()
        self.mock_github_service.amend_team_permissions_for_repository.assert_has_calls = (
            [
                call(12345, "admin", "some-repo")
            ]
        )
        self.assertEqual(len(self.repo.teams), 1)

    @patch("github.Team")
    def test_make_admin_team_on_github(self, mock_github_team):
        mock_github_team.name = "some-repo-write-team"
        self.repo.add_team(mock_github_team)
        self.assertEqual(len(self.repo.teams), 1)
        self.mock_github_service.team_exists.return_value = False
        self.mock_github_service.get_team_id_from_team_name.return_value = 12345
        mock_github_team.name = "some-repo-admin-team"
        self.mock_github_service.get_repository_teams.return_value = [
            mock_github_team]
        self.repo.ensure_repository_teams_exists()
        self.mock_github_service.amend_team_permissions_for_repository.assert_has_calls = (
            [
                call(12345, "admin", "some-repo")
            ]
        )
        self.assertEqual(len(self.repo.teams), 2)


class TestRepository4(unittest.TestCase):

    # Refactor Status: Done
    # Not needed
    def setUp(self):
        self.mock_github_service = MagicMock(GithubService)
        self.repo = Repository(
            self.mock_github_service,
            "some-repo",
            True,
            [],
            [],
            ["ignore_team"]
        )

        self.mock_github_service.get_user_permission_for_repository.return_value = "read"
        self.repo.direct_users = ["user1"]

    # Refactor Status: Done
    # Test moved to test_put_users_into_repository_teams_as_a_maintainer_as_team_empty()
    @patch("github.Team")
    def test_put_direct_users_into_non_admin_team_as_maintainer(self, mock_github_team):
        mock_github_team.name = "some-repo-read-team"
        self.repo.add_team(mock_github_team)
        self.repo.put_direct_users_into_teams()
        self.mock_github_service.add_user_to_team_as_maintainer.assert_called_once()
        self.mock_github_service.add_user_to_team.assert_not_called()

    # Refactor Status: Done
    # Test moved to test_put_users_into_repository_teams_as_a_user()
    @patch("github.Team")
    @patch("github.NamedUser")
    def test_put_direct_users_into_non_admin_team(self, mock_github_team, mock_named_user):
        mock_github_team.name = "some-repo-read-team"
        mock_named_user.login = "user1"
        mock_github_team.get_members.return_value = [mock_named_user]
        self.repo.add_team(mock_github_team)
        self.repo.put_direct_users_into_teams()
        self.mock_github_service.add_user_to_team_as_maintainer.assert_not_called()
        self.mock_github_service.add_user_to_team.assert_called_once()

    def test_create_repo_issue(self):
        self.repo.create_repo_issues_for_direct_users()
        self.mock_github_service.create_an_access_removed_issue_for_user_in_repository.assert_called_once_with(
            "user1", "some-repo")

    # Refactor Status: Done
    # Test moved to test_remove_repository_users_with_team_access()
    def test_remove_direct_users_access(self):
        self.repo.remove_direct_users_access()
        self.mock_github_service.remove_user_from_repository.assert_called_once_with(
            "user1", "some-repo")

    # Refactor Status: Done
    # Test moved to test_get_repository_teams_when_no_teams_exist()
    def test_get_existing_teams_when_repo_has_no_teams(self):
        self.mock_github_service.get_repository_teams.return_value = []
        self.repo.get_existing_teams()
        self.assertEqual(len(self.repo.teams), 0)

    # Refactor Status: Done
    # Test moved to test_get_repository_teams_when_team_is_in_ignore_list()
    @patch("github.Team")
    def test_get_existing_teams_when_repo_teams_is_ignored(self, mock_github_team):
        mock_github_team.name = "ignore_team"
        self.mock_github_service.get_repository_teams.return_value = [
            mock_github_team]
        self.repo.get_existing_teams()
        self.assertEqual(len(self.repo.teams), 0)

    # Refactor Status: Done
    # Test moved to test_get_repository_teams_when_team_is_in_ignore_list()
    @patch("github.Team")
    def test_get_existing_teams_when_repo_team_exists(self, mock_github_team):
        mock_github_team.name = "some-repo-maintain-team"
        self.mock_github_service.get_repository_teams.return_value = [
            mock_github_team]
        self.repo.get_existing_teams()
        self.assertEqual(len(self.repo.teams), 1)

    # Refactor Status: Done
    # Test not needed
    def test_do_not_remove_user_when_no_teams_exists(self):
        self.assertEqual(len(self.repo.direct_users), 1)
        self.repo.remove_users_already_in_existing_teams()
        self.assertEqual(len(self.repo.direct_users), 1)

    # Refactor Status: Done
    # Test not needed
    @patch("github.Team")
    def test_do_not_remove_user_when_teams_exist_but_user_isnt_in_team(self, mock_github_team):
        mock_github_team.name = "some-repo-maintain-team"
        self.mock_github_service.get_repository_teams.return_value = [
            mock_github_team]
        self.repo.get_existing_teams()
        self.assertEqual(len(self.repo.direct_users), 1)
        self.repo.remove_users_already_in_existing_teams()
        self.assertEqual(len(self.repo.direct_users), 1)

    # Refactor Status: Done
    # Test moved to test_remove_repository_users_with_team_access_when_repo_user_doesnt_have_access()
    @patch("python.lib.repository.RepositoryTeam")
    def test_do_not_remove_user_when_teams_exist_but_user_permission_doesnt_match_the_team(self, mock_repository_team):
        mock_repository_team.name = "other-team"
        mock_repository_team.users_usernames = ["user1"]
        mock_repository_team.permission = "write"
        self.repo.teams.append(mock_repository_team)
        self.assertEqual(len(self.repo.direct_users), 1)
        self.repo.remove_users_already_in_existing_teams()
        self.assertEqual(len(self.repo.direct_users), 1)

    # Refactor Status: Done
    # Test not needed
    @patch("python.lib.repository.RepositoryTeam")
    def test_remove_user_when_teams_exist_and_user_permission_matches_the_team_do_not_create_issue_on_repo(self, mock_repository_team):
        mock_repository_team.name = "other-team"
        mock_repository_team.users_usernames = ["user1"]
        mock_repository_team.repository_permission = "read"
        self.repo.teams.append(mock_repository_team)
        self.repo.issue_section_enabled = False
        self.assertEqual(len(self.repo.direct_users), 1)
        self.repo.remove_users_already_in_existing_teams()
        self.assertEqual(len(self.repo.direct_users), 0)
        self.mock_github_service.create_an_access_removed_issue_for_user_in_repository.assert_not_called()
        self.mock_github_service.remove_user_from_repository.assert_called_once_with(
            "user1", "some-repo")

    # Refactor Status: Done
    # Test moved to test_remove_repository_users_with_team_access()
    @patch("python.lib.repository.RepositoryTeam")
    def test_remove_user_when_teams_exist_and_user_permission_matches_the_team(self, mock_repository_team):
        mock_repository_team.name = "other-team"
        mock_repository_team.users_usernames = ["user1"]
        mock_repository_team.repository_permission = "read"
        self.repo.teams.append(mock_repository_team)
        self.assertEqual(len(self.repo.direct_users), 1)
        self.repo.remove_users_already_in_existing_teams()
        self.assertEqual(len(self.repo.direct_users), 0)
        self.mock_github_service.create_an_access_removed_issue_for_user_in_repository.assert_called_once_with(
            "user1", "some-repo")
        self.mock_github_service.remove_user_from_repository.assert_called_once_with(
            "user1", "some-repo")


class TestRepository5(unittest.TestCase):

    # Refactor Status: Done
    # Test not needed
    def setUp(self):
        self.mock_github_service = MagicMock(GithubService)
        self.repo = Repository(
            self.mock_github_service,
            "some-repo",
            False,
            [],
            ["ops-eng-user1"],
            []
        )
        self.repo.direct_users = ["user1"]

    def test_do_not_create_repo_issues_when_repo_issue_section_disabled(self):
        self.repo.create_repo_issues_for_direct_users()
        self.mock_github_service.create_an_access_removed_issue_for_user_in_repository.assert_not_called()

    # remove_operations_engineering_team_users_from_team
    def test_remove_operations_engineering_team_users_from_team(self):
        self.repo.remove_operations_engineering_team_users_from_team(12345)
        self.mock_github_service.remove_user_from_team.assert_called_once_with(
            "ops-eng-user1", 12345)

    # Refactor Status: Done
    # Test not needed
    def test_move_remaining_users_to_new_teams(self):
        self.repo.ensure_repository_teams_exists = MagicMock()
        self.repo.put_direct_users_into_teams = MagicMock()
        self.repo.create_repo_issues_for_direct_users = MagicMock()
        self.repo.remove_direct_users_access = MagicMock()
        self.repo.move_remaining_users_to_new_teams()
        self.repo.ensure_repository_teams_exists.assert_called_once()
        self.repo.put_direct_users_into_teams.assert_called_once()
        self.repo.create_repo_issues_for_direct_users.assert_called_once()
        self.repo.remove_direct_users_access.assert_called_once()

    # Refactor Status: Done
    # Test not needed
    def test_move_direct_users_to_teams(self):
        self.repo.remove_users_already_in_existing_teams = MagicMock()
        self.repo.move_remaining_users_to_new_teams = MagicMock()
        self.repo.move_direct_users_to_teams()
        self.repo.remove_users_already_in_existing_teams.assert_called_once()
        self.repo.move_remaining_users_to_new_teams.assert_called_once()


if __name__ == "__main__":
    unittest.main()
