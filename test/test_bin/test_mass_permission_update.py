import os
import unittest
from unittest.mock import patch, MagicMock, mock_open
import json
from bin.mass_permission_update import main, get_environment_variables, read_repository_list, parse_arguments


class TestGetEnvironmentVariables(unittest.TestCase):
    @patch.dict(os.environ, {"GITHUB_TOKEN": "token", "GITHUB_ORG_NAME": "test_org"})
    def test_returns_variables(self):
        org_token, org_name = get_environment_variables()
        self.assertEqual(org_token, "token")
        self.assertEqual(org_name, "test_org")

    @patch.dict(os.environ, {"GITHUB_TOKEN": "token"})
    def test_returns_default_variables(self):
        org_token, org_name = get_environment_variables()
        self.assertEqual(org_token, "token")
        self.assertEqual(org_name, "ministryofjustice")

    def test_raises_error_when_no_github_token(self):
        self.assertRaises(
            ValueError, get_environment_variables)


class TestReadRepositoryList(unittest.TestCase):
    @patch("builtins.open", new_callable=mock_open, read_data='[{"name": "repo1"}, {"name": "repo2"}]')
    def test_read_repository_list_success(self, mock_file):
        repos = read_repository_list("repositories.json")
        self.assertEqual(repos, [{"name": "repo1"}, {"name": "repo2"}])
        mock_file.assert_called_with(file="repositories.json", mode='r', encoding='utf-8')

    @patch("builtins.open", side_effect=FileNotFoundError)
    def test_read_repository_list_file_not_found(self, _mock_file):
        with self.assertRaises(FileNotFoundError):
            read_repository_list("repositories.json")

    @patch("builtins.open", new_callable=mock_open, read_data='Invalid JSON')
    def test_read_repository_list_json_decode_error(self, _mock_file):
        with self.assertRaises(json.JSONDecodeError):
            read_repository_list("repositories.json")


class TestParseArguments(unittest.TestCase):
    def test_parse_arguments(self):
        test_args = ["script_name", "team_name", "read"]
        with patch("sys.argv", test_args):
            args = parse_arguments()
            self.assertEqual(args.team_name, "team_name")
            self.assertEqual(args.permission_level, "read")


@patch("services.github_service.GithubService.__new__")
@patch.dict(os.environ, {"GITHUB_TOKEN": "token", "GITHUB_ORG_NAME": "test_org"})
class TestMain(unittest.TestCase):

    @patch("builtins.open", new_callable=mock_open, read_data='[{"name": "repo1"}, {"name": "repo2"}]')
    def test_main_updates_permissions(self, _mock_file, mock_github_service: MagicMock):
        mock_github_service.return_value.update_team_repository_permission.return_value = None
        test_args = ["script_name", "team_name", "admin"]
        with patch("sys.argv", test_args):
            main()
            mock_github_service.return_value.update_team_repository_permission.assert_called_once_with(
                "team_name", [{"name": "repo1"}, {"name": "repo2"}], "admin"
            )

    @patch("builtins.open", new_callable=mock_open, read_data='[{"name": "repo1"}, {"name": "repo2"}]')
    def test_main_file_not_found(self, mock_file, _mock_github_service: MagicMock):
        mock_file.side_effect = FileNotFoundError
        test_args = ["script_name", "team_name", "admin"]
        with patch("sys.argv", test_args):
            with self.assertRaises(FileNotFoundError):
                main()

    @patch("builtins.open", new_callable=mock_open, read_data='Invalid JSON')
    def test_main_json_decode_error(self, mock_file, _mock_github_service: MagicMock):
        mock_file.side_effect = json.JSONDecodeError("Expecting value", "doc", 0)
        test_args = ["script_name", "team_name", "admin"]
        with patch("sys.argv", test_args):
            with self.assertRaises(json.JSONDecodeError):
                main()


if __name__ == "__main__":
    unittest.main()
