import unittest
import python.scripts.dormant_users
from unittest.mock import patch, MagicMock

from python.scripts.unowned_repositories import (
    main,
    get_cli_arguments,
    get_org_teams,
    check_the_repositories
)

@patch("python.scripts.unowned_repositories.GithubService", new=MagicMock)
@patch("python.scripts.unowned_repositories.SlackService", new=MagicMock)
@patch("python.scripts.unowned_repositories.get_cli_arguments")
@patch("python.scripts.unowned_repositories.check_the_repositories")
class TestUnownedRepositoriesMain(unittest.TestCase):
    def test_main_runs_step_one(self, mock_check_the_repositories, mock_get_cli_arguments):
        mock_get_cli_arguments.return_value = "", "", ""
        main()
        mock_check_the_repositories.assert_called_once()
        mock_get_cli_arguments.assert_called_once()

class TestUnownedRepositories(unittest.TestCase):
    @patch("sys.argv", ["", "", "", ""])
    def test_get_cli_arguments_correct_length(self):
        args = get_cli_arguments()
        self.assertEqual(len(args), 3)

    @patch("sys.argv", [""])
    def test_get_cli_arguments_raises_error(self):
        self.assertRaises(
            ValueError, get_cli_arguments)

    @patch("python.services.github_service.GithubService")
    def test_get_org_teams_no_teams_exist(self, mock_github_service):
        mock_github_service.get_team_names.return_value = []
        teams = get_org_teams(mock_github_service)
        self.assertEqual(len(teams), 0)

    @patch("python.services.github_service.GithubService")
    def test_get_org_teams_ignore_teams(self, mock_github_service):
        mock_github_service.get_team_names.return_value = ["all-org-members"]
        teams = get_org_teams(mock_github_service)
        self.assertEqual(len(teams), 0)

        mock_github_service.get_team_names.return_value = ["organisation-security-auditor"]
        teams = get_org_teams(mock_github_service)
        self.assertEqual(len(teams), 0)

    @patch("python.services.github_service.GithubService")
    def test_get_org_teams(self, mock_github_service):
        mock_github_service.get_team_names.return_value = ["some-team"]
        mock_github_service.get_team_repository_names.return_value = ["some-repo"]
        mock_github_service.get_team_user_names.return_value = ["some-user"]
        expected_result = {
            "name": "some-team",
            "repositories": ["some-repo"],
            "number_of_users": 1
        }
        teams = get_org_teams(mock_github_service)
        self.assertEqual(len(teams), 1)
        self.assertEqual(teams[0], expected_result)

    @patch("python.services.github_service.GithubService")
    @patch("python.scripts.unowned_repositories.get_org_teams")
    def test_check_the_repositories_when_no_org_repositories_exist(self, mock_get_org_teams, mock_github_service):
        mock_get_org_teams.return_value = []
        mock_github_service.get_org_repo_names.return_value = []
        check_the_repositories(mock_github_service)
        mock_github_service.get_repository_collaborators.assert_not_called()

    @patch("python.services.github_service.GithubService")
    @patch("python.scripts.unowned_repositories.get_org_teams")
    def test_check_the_repositories_when_repo_has_a_collaborator(self, mock_get_org_teams, mock_github_service):
        mock_get_org_teams.return_value = []
        mock_github_service.get_repository_collaborators.return_value = ["some-collaborator"]
        mock_github_service.get_org_repo_names.return_value = ["org-repo"]
        check_the_repositories(mock_github_service)
        mock_github_service.get_repository_collaborators.assert_called()

    @patch("python.services.github_service.GithubService")
    @patch("python.scripts.unowned_repositories.get_org_teams")
    def test_check_the_repositories_when_repo_has_no_collaborators(self, mock_get_org_teams, mock_github_service):
        mock_get_org_teams.return_value = []
        mock_github_service.get_repository_collaborators.return_value = []
        mock_github_service.get_org_repo_names.return_value = ["org-repo"]
        check_the_repositories(mock_github_service)
        mock_github_service.get_repository_collaborators.assert_called()

    @patch("python.services.github_service.GithubService")
    @patch("python.scripts.unowned_repositories.get_org_teams")
    def test_check_the_repositories_when_no_matching_org_repository_exists(self, mock_get_org_teams, mock_github_service):
        team = {
            "name": "some-team",
            "repositories": ["some-repo"],
            "number_of_users": 1
        }
        mock_get_org_teams.return_value = [team]
        mock_github_service.get_repository_collaborators.return_value = []
        mock_github_service.get_org_repo_names.return_value = ["org-repo"]
        check_the_repositories(mock_github_service)
        mock_github_service.get_repository_collaborators.assert_called()

    @patch("python.services.github_service.GithubService")
    @patch("python.scripts.unowned_repositories.get_org_teams")
    def test_check_the_repositories_when_repo_has_a_team(self, mock_get_org_teams, mock_github_service):
        team = {
            "name": "some-team",
            "repositories": ["org-repo"],
            "number_of_users": 1
        }
        mock_get_org_teams.return_value = [team]
        mock_github_service.get_repository_collaborators.return_value = []
        mock_github_service.get_org_repo_names.return_value = ["org-repo"]
        check_the_repositories(mock_github_service)
        mock_github_service.get_repository_collaborators.assert_not_called()


if __name__ == "__main__":
    unittest.main()
