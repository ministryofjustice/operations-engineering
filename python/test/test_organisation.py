import os
import json
import unittest
from unittest.mock import MagicMock, patch

from python.services.github_service import GithubService
from python.lib.organisation import Organisation


class TestOrganisation(unittest.TestCase):

    def test_detect_config_file_env_var_missing(self):
        mock_github_service = MagicMock(GithubService)
        with self.assertRaises(ValueError):
            Organisation(mock_github_service, "some-org")


@patch.dict(os.environ, {"CONFIG_FILE": "test/files/some-config.yml"})
class TestOrganisation1(unittest.TestCase):

    def test_provide_wrong_config_file(self):
        mock_github_service = MagicMock(GithubService)
        with self.assertRaises(ValueError):
            Organisation(mock_github_service, "some-org")


@patch.dict(os.environ, {"CONFIG_FILE": "test/files/incorrect-config1.yml"})
class TestOrganisation2(unittest.TestCase):

    def test_provide_incorrect_config_file_1(self):
        mock_github_service = MagicMock(GithubService)
        with self.assertRaises(KeyError):
            Organisation(mock_github_service, "some-org")


@patch.dict(os.environ, {"CONFIG_FILE": "test/files/incorrect-config2.yml"})
class TestOrganisation3(unittest.TestCase):

    def test_provide_incorrect_config_file_2(self):
        mock_github_service = MagicMock(GithubService)
        with self.assertRaises(KeyError):
            Organisation(mock_github_service, "some-org")


@patch.dict(os.environ, {"CONFIG_FILE": "test/files/test-config.yml"})
class TestOrganisation5(unittest.TestCase):

    def test_smoke_test(self):
        mock_github_service = MagicMock(GithubService)

        mock_github_service.get_outside_collaborators_login_names.return_value = []
        mock_github_service.get_a_team_usernames.return_value = []
        mock_github_service.get_paginated_list_of_repositories_per_type.return_value = {
            "search": {
                "repos": [],
                "pageInfo": {
                    "hasNextPage": False,
                    "endCursor": ""
                }
            }
        }
        mock_github_service.get_repository_direct_users.return_value = []
        org = Organisation(mock_github_service, "some-org")
        self.assertEqual(org.ignore_teams, ["ignoreteam1"])
        self.assertEqual(org.badly_named_repositories, ["repo1234"])
        self.assertEqual(org.repositories_with_direct_users, [])
        self.assertEqual(org.repositories, [])
        self.assertEqual(org.ops_eng_team_user_usernames, [])
        self.assertEqual(org.outside_collaborators, [])
        self.assertEqual(org.org_name, "some-org")
        self.assertEqual(org.outside_collaborators, [])


@patch.dict(os.environ, {"CONFIG_FILE": "test/files/test-config.yml"})
class TestOrganisation6(unittest.TestCase):

    def test_filter_ignored_repo(self):
        mock_github_service = MagicMock(GithubService)

        mock_github_service.get_outside_collaborators_login_names.return_value = []
        mock_github_service.get_a_team_usernames.return_value = []
        mock_github_service.get_paginated_list_of_repositories_per_type.return_value = {
            "search": {
                "repos": [
                    {
                        "repo": {
                            "isDisabled": False,
                            "isLocked": False,
                            "name": "repo1",
                            "hasIssuesEnabled": False,
                            "collaborators": {
                                "totalCount": 1
                            }
                        }
                    },
                    {
                        "repo": {
                            "isDisabled": False,
                            "isLocked": False,
                            "name": "repo1234",
                            "hasIssuesEnabled": False,
                            "collaborators": {
                                "totalCount": 1
                            }
                        }
                    }
                ],
                "pageInfo": {
                    "hasNextPage": False,
                    "endCursor": ""
                }
            }
        }
        mock_github_service.get_repository_direct_users.return_value = []
        org = Organisation(mock_github_service, "some-org")
        self.assertEqual(org.repositories, [
                         ('repo1', False, 1), ('repo1', False, 1), ('repo1', False, 1)])


if __name__ == "__main__":
    unittest.main()
