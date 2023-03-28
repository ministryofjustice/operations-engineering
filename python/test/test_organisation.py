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

        mock_github_service.get_paginated_list_of_repositories.return_value = {
            "organization": {
                "repositories": {
                    "pageInfo": {"endCursor": "some-value", "hasNextPage": False},
                    "edges": [
                        {
                            "node": {
                                "name": "repo1",
                                "isDisabled": False,
                                "isArchived": False,
                                "isLocked": False,
                                "hasIssuesEnabled": True,
                            }
                        },
                        {
                            "node": {
                                "name": "repo2",
                                "isDisabled": False,
                                "isArchived": False,
                                "isLocked": False,
                                "hasIssuesEnabled": True,
                            }
                        },
                        {
                            "node": {
                                "name": "repo3",
                                "isDisabled": False,
                                "isArchived": False,
                                "isLocked": False,
                                "hasIssuesEnabled": True,
                            }
                        },
                        {
                            "node": {
                                "name": "repo4",
                                "isDisabled": False,
                                "isArchived": False,
                                "isLocked": False,
                                "hasIssuesEnabled": True,
                            }
                        },
                    ],
                }
            }
        }

        mock_github_service.get_paginated_list_of_user_names_and_permissions_with_direct_access_to_repository.return_value = {
            "repository": {
                "collaborators": {
                    "edges": [
                        {"node": {"login": "some-user1"}, "permission": "ADMIN"},
                        {"node": {"login": "some-user2"}, "permission": "WRITE"},
                        {"node": {"login": "some-user3"}, "permission": "MAINTAIN"},
                        {"node": {"login": "some-user4"}, "permission": "READ"},
                        {"node": {"login": "collaborator1"}, "permission": "WRITE"},
                    ],
                    "pageInfo": {"hasNextPage": False, "endCursor": "some-value"},
                }
            }
        }

        mock_github_service.get_paginated_list_of_team_names.return_value = {
            "organization": {
                "teams": {
                    "pageInfo": {"endCursor": "some-value", "hasNextPage": False},
                    "edges": [
                        {"node": {"slug": "repo1-admin-team"}},
                        {"node": {"slug": "repo2-admin-team"}},
                        {"node": {"slug": "ignoreteam1"}},
                    ],
                }
            }
        }

        mock_github_service.get_paginated_list_of_team_user_names.return_value = {
            "organization": {
                "team": {
                    "members": {
                        "edges": [
                            {"node": {"login": "some-user1"}},
                            {"node": {"login": "some-user2"}},
                        ],
                        "pageInfo": {"hasNextPage": False, "endCursor": "some-value"},
                    }
                }
            }
        }

        mock_github_service.get_paginated_list_of_team_repositories_and_permissions.return_value = {
            "organization": {
                "team": {
                    "repositories": {
                        "edges": [
                            {"node": {"name": "repo1"}, "permission": "ADMIN"},
                            {"node": {"name": "repo2"}, "permission": "WRITE"},
                            {"node": {"name": "repo3"}, "permission": "MAINTAIN"},
                            {"node": {"name": "repo4"}, "permission": "READ"},
                        ],
                        "pageInfo": {"endCursor": "some-value", "hasNextPage": False},
                    }
                }
            }
        }

        mock_github_service.get_team_id_from_team_name.return_value = 1234

        org = Organisation(mock_github_service, "some-org")
        org.check_users_access()


if __name__ == "__main__":
    unittest.main()
