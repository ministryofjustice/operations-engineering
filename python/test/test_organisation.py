import os
import json
import unittest
from unittest.mock import MagicMock, patch, call

from python.services.github_service import GithubService
from python.lib.organisation import Organisation
from python.lib.repository import Repository


class TestOrganisation1(unittest.TestCase):

    def test_detect_config_file_env_var_missing(self):
        mock_github_service = MagicMock(GithubService)
        with self.assertRaises(ValueError):
            Organisation(mock_github_service, "some-org")

    @patch.dict(os.environ, {"CONFIG_FILE": "test/files/some-config.yml"})
    def test_provide_wrong_config_file(self):
        mock_github_service = MagicMock(GithubService)
        with self.assertRaises(ValueError):
            Organisation(mock_github_service, "some-org")

    @patch.dict(os.environ, {"CONFIG_FILE": "test/files/incorrect-config1.yml"})
    def test_provide_incorrect_config_file_1(self):
        mock_github_service = MagicMock(GithubService)
        with self.assertRaises(KeyError):
            Organisation(mock_github_service, "some-org")

    @patch.dict(os.environ, {"CONFIG_FILE": "test/files/incorrect-config2.yml"})
    def test_provide_incorrect_config_file_2(self):
        mock_github_service = MagicMock(GithubService)
        with self.assertRaises(KeyError):
            Organisation(mock_github_service, "some-org")


@patch.dict(os.environ, {"CONFIG_FILE": "test/files/test-config.yml"})
class TestOrganisation2(unittest.TestCase):

    def setUp(self):
        self.mock_github_service = MagicMock(GithubService)

        self.mock_github_service.get_outside_collaborators_login_names.return_value = []
        self.mock_github_service.get_a_team_usernames.return_value = []
        self.mock_github_service.get_repository_direct_users.return_value = []

    def test_smoke_test(self):
        self.mock_github_service.get_paginated_list_of_repositories_per_type.return_value = {
            "search": {
                "repos": [],
                "pageInfo": {
                    "hasNextPage": False,
                    "endCursor": ""
                }
            }
        }

        org = Organisation(self.mock_github_service, "some-org")
        self.assertEqual(org.ignore_teams, ["ignoreteam1"])
        self.assertEqual(org.badly_named_repositories, ["repo1234"])
        self.assertEqual(org.repositories_with_direct_users, [])
        self.assertEqual(org.repositories, [])
        self.assertEqual(org.ops_eng_team_user_usernames, [])
        self.assertEqual(org.org_name, "some-org")

    def test_filter_out_ignored_repos(self):
        self.mock_github_service.get_paginated_list_of_repositories_per_type.return_value = {
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
        org = Organisation(self.mock_github_service, "some-org")
        # Creates three repo's: x1 public, x1 private and x1 internal
        self.assertEqual(org.repositories, [
                         ('repo1', False, 1), ('repo1', False, 1), ('repo1', False, 1)])

    def test_ignore_disabled_repo(self):
        self.mock_github_service.get_paginated_list_of_repositories_per_type.return_value = {
            "search": {
                "repos": [
                    {
                        "repo": {
                            "isDisabled": True,
                            "isLocked": False,
                            "name": "repo1",
                            "hasIssuesEnabled": False,
                            "collaborators": {
                                "totalCount": 1
                            }
                        }
                    },
                ],
                "pageInfo": {
                    "hasNextPage": False,
                    "endCursor": ""
                }
            }
        }
        org = Organisation(self.mock_github_service, "some-org")
        self.assertEqual(len(org.repositories), 0)

    def test_ignore_locked_repo(self):
        self.mock_github_service.get_paginated_list_of_repositories_per_type.return_value = {
            "search": {
                "repos": [
                    {
                        "repo": {
                            "isDisabled": False,
                            "isLocked": True,
                            "name": "repo1",
                            "hasIssuesEnabled": False,
                            "collaborators": {
                                "totalCount": 1
                            }
                        }
                    },
                ],
                "pageInfo": {
                    "hasNextPage": False,
                    "endCursor": ""
                }
            }
        }
        org = Organisation(self.mock_github_service, "some-org")
        self.assertEqual(len(org.repositories), 0)

    def test_dont_create_repo_object_when_no_direct_users(self):
        self.mock_github_service.get_paginated_list_of_repositories_per_type.return_value = {
            "search": {
                "repos": [
                    {
                        "repo": {
                            "isDisabled": False,
                            "isLocked": False,
                            "name": "repo1",
                            "hasIssuesEnabled": False,
                            "collaborators": {
                                "totalCount": 0
                            }
                        }
                    },
                ],
                "pageInfo": {
                    "hasNextPage": False,
                    "endCursor": ""
                }
            }
        }
        org = Organisation(self.mock_github_service, "some-org")
        self.assertEqual(len(org.repositories_with_direct_users), 0)


@patch.dict(os.environ, {"CONFIG_FILE": "test/files/test-config.yml"})
class TestOrganisation3(unittest.TestCase):

    def test_filter_out_outside_collaborators(self):
        mock_github_service = MagicMock(GithubService)

        mock_github_service.get_outside_collaborators_login_names.return_value = [
            "user1234"]
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
                ],
                "pageInfo": {
                    "hasNextPage": False,
                    "endCursor": ""
                }
            }
        }
        mock_github_service.get_repository_direct_users.return_value = [
            "user1", "user1234"]
        org = Organisation(mock_github_service, "some-org")
        for repo in org.repositories_with_direct_users:
            self.assertEqual(len(repo.direct_users), 1)


@patch.dict(os.environ, {"CONFIG_FILE": "test/files/test-config.yml"})
class TestOrganisation4(unittest.TestCase):

    def setUp(self):
        self.mock_github_service = MagicMock(GithubService)

        self.mock_github_service.get_outside_collaborators_login_names.return_value = []
        self.mock_github_service.get_a_team_usernames.return_value = []
        self.mock_github_service.get_paginated_list_of_repositories_per_type.return_value = {
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
                ],
                "pageInfo": {
                    "hasNextPage": False,
                    "endCursor": ""
                }
            }
        }
        self.mock_github_service.get_repository_direct_users.return_value = [
            "user1"]

    @patch("python.lib.repository.Repository.__new__")
    def test_create_repo_object(self, mock_repository):
        org = Organisation(self.mock_github_service, "some-org")
        # Creates three repo's x1 public, x1 private and x1 internal
        self.assertEqual(len(org.repositories_with_direct_users), 3)

    @patch("python.lib.repository.Repository.__new__")
    def test_call_close_expired_issues(self, mock_repository):
        org = Organisation(self.mock_github_service, "some-org")
        org.close_expired_issues()
        self.mock_github_service.close_expired_issues.assert_has_calls(
            [
                call("repo1"),
                call("repo1"),
                call("repo1")
            ]
        )

    @patch("python.lib.repository.Repository.__new__")
    def test_call_move_users_to_teams(self, mock_repository):
        org = Organisation(self.mock_github_service, "some-org")
        org.move_users_to_teams()
        mock_repository.move_direct_users_to_teams.assert_has_calls
        (
            [
                call(),
                call(),
                call()
            ]
        )


if __name__ == "__main__":
    unittest.main()
