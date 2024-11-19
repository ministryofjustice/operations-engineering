import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, Mock, call, patch

from freezegun import freeze_time
from github import (Github, GithubException, RateLimitExceededException,
                    UnknownObjectException)
from github.Branch import Branch
from github.NamedUser import NamedUser
from github.Organization import Organization
from github.Repository import Repository
from github.Variable import Variable
from gql.transport.exceptions import TransportServerError

from services.github_service import (
    GithubService, retries_github_rate_limit_exception_at_next_reset_once)

# pylint: disable=E1101

ORGANISATION_NAME = "moj-analytical-services"
ENTERPRISE_NAME = "ministry-of-justice-uk"
USER_ACCESS_REMOVED_ISSUE_TITLE = "User access removed, access is now via a team"
TEST_REPOSITORY = "moj-analytical-services/test_repository"


class TestRetriesGithubRateLimitExceptionAtNextResetOnce(unittest.TestCase):

    def test_function_is_only_called_once_with_arguments(self):
        mock_function = Mock()
        mock_github_client = Mock(Github)
        mock_github_service = Mock(
            GithubService, github_client_core_api=mock_github_client)
        retries_github_rate_limit_exception_at_next_reset_once(
            mock_function)(mock_github_service, "test_arg")
        mock_function.assert_has_calls(
            [call(mock_github_service, "test_arg")])

    @freeze_time("2023-02-01")
    def test_function_is_called_twice_when_rate_limit_exception_raised_once(self):
        mock_function = Mock(
            side_effect=[RateLimitExceededException(Mock(), Mock(), Mock()), Mock()])
        mock_github_client = Mock(Github)
        mock_github_client.get_rate_limit().core.reset = datetime.now()
        mock_github_service = Mock(
            GithubService, github_client_core_api=mock_github_client)
        retries_github_rate_limit_exception_at_next_reset_once(
            mock_function)(mock_github_service, "test_arg")
        mock_function.assert_has_calls([call(mock_github_service, 'test_arg')])

    @freeze_time("2023-02-01")
    def test_rate_limit_exception_raised_when_rate_limit_exception_raised_twice(self):
        mock_function = Mock(side_effect=[
            RateLimitExceededException(Mock(), Mock(), Mock()),
            RateLimitExceededException(Mock(), Mock(), Mock())]
        )
        mock_github_client = Mock(Github)
        mock_github_client.get_rate_limit().core.reset = datetime.now()
        mock_github_service = Mock(
            GithubService, github_client_core_api=mock_github_client)
        self.assertRaises(RateLimitExceededException,
                          retries_github_rate_limit_exception_at_next_reset_once(
                              mock_function), mock_github_service,
                          "test_arg")

    @freeze_time("2023-02-01")
    def test_function_is_called_twice_when_transport_server_error_raised_once(self):
        mock_function = Mock(
            side_effect=[TransportServerError(Mock(), Mock()), Mock()])
        mock_github_client = Mock(Github)
        mock_github_client.get_rate_limit().graphql.reset = datetime.now()
        mock_github_service = Mock(
            GithubService, github_client_core_api=mock_github_client)
        retries_github_rate_limit_exception_at_next_reset_once(
            mock_function)(mock_github_service, "test_arg")
        mock_function.assert_has_calls([call(mock_github_service, 'test_arg')])

    @freeze_time("2023-02-01")
    def test_rate_limit_exception_raised_when_transport_query_error_raised_twice(self):
        mock_function = Mock(side_effect=[
            TransportServerError(Mock(), Mock()),
            TransportServerError(Mock(), Mock())]
        )
        mock_github_client = Mock(Github)
        mock_github_client.get_rate_limit().graphql.reset = datetime.now()
        mock_github_service = Mock(
            GithubService, github_client_core_api=mock_github_client)
        self.assertRaises(TransportServerError,
                          retries_github_rate_limit_exception_at_next_reset_once(
                              mock_function), mock_github_service,
                          "test_arg")


@patch("gql.transport.aiohttp.AIOHTTPTransport.__new__", new=MagicMock)
@patch("gql.Client.__new__")
@patch("github.Github.__new__")
@patch("requests.sessions.Session.__new__")
class TestGithubServiceInit(unittest.TestCase):

    def test_sets_up_class(self,  mock_github_client_rest_api, mock_github_client_core_api, mock_github_client_gql_api):
        mock_github_client_core_api.return_value = "test_mock_github_client_core_api"
        mock_github_client_gql_api.return_value = "test_mock_github_client_gql_api"
        github_service = GithubService("", ORGANISATION_NAME)
        self.assertEqual("test_mock_github_client_core_api",
                         github_service.github_client_core_api)
        self.assertEqual("test_mock_github_client_gql_api",
                         github_service.github_client_gql_api)
        mock_github_client_rest_api.assert_has_calls([call().headers.update(
            {'Accept': 'application/vnd.github+json', 'Authorization': 'Bearer '})])
        self.assertEqual(ORGANISATION_NAME,
                         github_service.organisation_name)
        self.assertEqual(ENTERPRISE_NAME,
                         github_service.enterprise_name)


@patch("gql.transport.aiohttp.AIOHTTPTransport.__new__", new=MagicMock)
@patch("gql.Client.__new__", new=MagicMock)
@patch("github.Github.__new__")
class TestGithubServiceGetOutsideCollaborators(unittest.TestCase):

    def test_returns_login_names(self, mock_github_client_core_api):
        mock_github_client_core_api.return_value.get_organization().get_outside_collaborators.return_value = [
            Mock(NamedUser, login="tom-smith"),
            Mock(NamedUser, login="john.smith"),
        ]
        response = GithubService(
            "", ORGANISATION_NAME).get_outside_collaborators_login_names()
        self.assertEqual(["tom-smith", "john.smith"], response)

    def test_calls_downstream_services(self, mock_github_client_core_api):
        mock_github_client_core_api.return_value.get_organization(
        ).get_outside_collaborators.return_value = []
        github_service = GithubService("", ORGANISATION_NAME)
        github_service.get_outside_collaborators_login_names()
        github_service.github_client_core_api.get_organization.assert_has_calls(
            [call(), call(ORGANISATION_NAME), call().get_outside_collaborators()])

    def test_returns_empty_list_when_collaborators_returns_none(self, mock_github_client_core_api):
        mock_github_client_core_api.return_value.get_organization(
        ).get_outside_collaborators.return_value = None
        github_service = GithubService("", ORGANISATION_NAME)
        response = github_service.get_outside_collaborators_login_names()
        self.assertEqual([], response)

    def test_returns_exception_when_collaborators_returns_exception(self, mock_github_client_core_api):
        mock_github_client_core_api.return_value.get_organization(
        ).get_outside_collaborators.side_effect = ConnectionError
        github_service = GithubService("", ORGANISATION_NAME)
        self.assertRaises(
            ConnectionError, github_service.get_outside_collaborators_login_names)

    def test_returns_exception_when_organization_returns_exception(self, mock_github_client_core_api):
        mock_github_client_core_api.return_value.get_organization.side_effect = ConnectionError
        github_service = GithubService("", ORGANISATION_NAME)
        self.assertRaises(
            ConnectionError, github_service.get_outside_collaborators_login_names)


@patch("gql.transport.aiohttp.AIOHTTPTransport.__new__", new=MagicMock)
@patch("gql.Client.__new__")
@patch("github.Github.__new__")
class TestGithubServiceAddAllUsersToTeam(unittest.TestCase):

    def __create_user(self, name: str) -> Mock:
        return Mock(NamedUser, name=name)

    def test_adds_users_not_currently_in_team(self, mock_github_client_core_api, mock_github_client_gql_api):
        user_1 = self.__create_user("user_1")
        user_2 = self.__create_user("user_2")
        user_3 = self.__create_user("user_3")
        user_4 = self.__create_user("user_4")
        mock_github_client_gql_api.return_value.execute.return_value = {
            "organization": {"team": {"databaseId": 1}}}
        mock_github_client_core_api.return_value.get_organization().get_members.return_value = [
            user_1, user_2, user_3, user_4
        ]
        mock_team = mock_github_client_core_api.return_value.get_organization().get_team()
        mock_team.get_members.return_value = [
            user_1, user_2,
        ]
        mock_github_client_core_api.return_value.get_user.side_effect = [
            user_3, user_4]

        github_service = GithubService("", ORGANISATION_NAME)
        github_service.add_all_users_to_team("test_team_name")
        mock_team.assert_has_calls(
            [call.add_membership(user_3), call.add_membership(user_4)])

    def test_adds_no_users_when_all_user_already_exist(self, mock_github_client_core_api, mock_github_client_gql_api):
        user_1 = self.__create_user("user_1")
        user_2 = self.__create_user("user_2")

        mock_github_client_gql_api.return_value.execute.return_value = {
            "organization": {"team": {"databaseId": 1}}}
        mock_github_client_core_api.return_value.get_organization().get_members.return_value = [
            user_1, user_2,
        ]
        mock_team = mock_github_client_core_api.return_value.get_organization().get_team()
        mock_team.get_members.return_value = [
            user_1, user_2
        ]

        GithubService("", ORGANISATION_NAME).add_all_users_to_team(
            "test_team_name")
        mock_team.add_membership.assert_not_called()

    def test_throws_exception_when_client_throws_exception(self, mock_github_client_core_api,
                                                           _mock_github_client_gql_api):
        mock_github_client_core_api.return_value.get_organization = MagicMock(
            side_effect=ConnectionError)
        github_service = GithubService("", ORGANISATION_NAME)
        self.assertRaises(
            ConnectionError, github_service.add_all_users_to_team, "test_team_name")


@patch("gql.transport.aiohttp.AIOHTTPTransport.__new__", new=MagicMock)
@patch("gql.Client.__new__")
@patch("github.Github.__new__", new=MagicMock)
class TestGithubServiceGetTeamIdFromTeamName(unittest.TestCase):
    def test_calls_downstream_services(self, _mock_gql_client):
        github_service = GithubService("", ORGANISATION_NAME)
        github_service.get_team_id_from_team_name("test_team_name")
        github_service.github_client_gql_api.assert_has_calls([
            call.execute().__getitem__('organization'),
            call.execute().__getitem__().__getitem__('team'),
            call.execute().__getitem__().__getitem__().__getitem__('databaseId')
        ])


@patch("gql.transport.aiohttp.AIOHTTPTransport.__new__", new=MagicMock)
@patch("gql.Client.__new__", new=MagicMock)
@patch("github.Github.__new__", new=MagicMock)
class TestGithubServiceGetPaginatedListOfOrgRepositoryNames(unittest.TestCase):
    def test_calls_downstream_services(self):
        github_service = GithubService("", ORGANISATION_NAME)
        github_service.get_paginated_list_of_org_repository_names(
            "test_after_cursor")
        github_service.github_client_gql_api.execute.assert_called_once()

    def test_throws_value_error_when_page_size_greater_than_limit(self):
        github_service = GithubService("", ORGANISATION_NAME)
        self.assertRaises(
            ValueError, github_service.get_paginated_list_of_org_repository_names, "test_after_cursor", 101)


@patch("gql.transport.aiohttp.AIOHTTPTransport.__new__", new=MagicMock)
@patch("gql.Client.__new__", new=MagicMock)
@patch("github.Github.__new__", new=MagicMock)
class TestGithubServiceGetPaginatedListOfUnlockedUnarchivedReposAndTheirFirst100OutsideCollaborators(unittest.TestCase):
    def test_calls_downstream_services(self):
        github_service = GithubService("", ORGANISATION_NAME)
        github_service.get_paginated_list_of_unlocked_unarchived_repos_and_their_first_100_outside_collaborators(
            "test_after_cursor"
        )
        github_service.github_client_gql_api.execute.assert_called_once()

    def test_throws_value_error_when_page_size_greater_than_limit(self):
        github_service = GithubService("", ORGANISATION_NAME)
        self.assertRaises(
            ValueError,
            github_service.get_paginated_list_of_unlocked_unarchived_repos_and_their_first_100_outside_collaborators,
            "test_after_cursor",
            101
        )


@patch("gql.transport.aiohttp.AIOHTTPTransport.__new__", new=MagicMock)
@patch("gql.Client.__new__", new=MagicMock)
@patch("github.Github.__new__", new=MagicMock)
class TestGithubServiceGetPaginatedListOfTeamNames(unittest.TestCase):
    def test_calls_downstream_services(self):
        github_service = GithubService("", ORGANISATION_NAME)
        github_service.get_paginated_list_of_team_names("test_after_cursor")
        github_service.github_client_gql_api.execute.assert_called_once()

    def test_throws_value_error_when_page_size_greater_than_limit(self):
        github_service = GithubService("", ORGANISATION_NAME)
        self.assertRaises(
            ValueError, github_service.get_paginated_list_of_team_names, "test_after_cursor", 101)


@patch("gql.transport.aiohttp.AIOHTTPTransport.__new__", new=MagicMock)
@patch("gql.Client.__new__", new=MagicMock)
@patch("github.Github.__new__", new=MagicMock)
class TestGithubServiceGetPaginatedListOfTeamRepositories(unittest.TestCase):
    def test_calls_downstream_services(self):
        github_service = GithubService("", ORGANISATION_NAME)
        github_service.get_paginated_list_of_team_repositories(
            "test_team_name", "test_after_cursor")
        github_service.github_client_gql_api.execute.assert_called_once()

    def test_throws_value_error_when_page_size_greater_than_limit(self):
        github_service = GithubService("", ORGANISATION_NAME)
        self.assertRaises(
            ValueError, github_service.get_paginated_list_of_team_repositories, "test_team_name", "test_after_cursor",
            101)


@patch("gql.transport.aiohttp.AIOHTTPTransport.__new__", new=MagicMock)
@patch("gql.Client.__new__", new=MagicMock)
@patch("github.Github.__new__", new=MagicMock)
class TestGithubServiceGetPaginatedListOfUserNames(unittest.TestCase):
    def test_calls_downstream_services(self):
        github_service = GithubService("", ORGANISATION_NAME)
        github_service.get_paginated_list_of_team_user_names(
            "test_team_name", "test_after_cursor")
        github_service.github_client_gql_api.execute.assert_called_once()

    def test_throws_value_error_when_page_size_greater_than_limit(self):
        github_service = GithubService("", ORGANISATION_NAME)
        self.assertRaises(
            ValueError, github_service.get_paginated_list_of_team_user_names, "test_team_name", "test_after_cursor",
            101)


@patch("gql.transport.aiohttp.AIOHTTPTransport.__new__", new=MagicMock)
@patch("gql.Client.__new__", new=MagicMock)
@patch("github.Github.__new__")
class TestGithubServiceGetRepositoryCollaborators(unittest.TestCase):

    def test_returns_direct_users(self, mock_github_client_core_api):
        mock_github_client_core_api.return_value.get_repo().get_collaborators.return_value = [
            Mock(NamedUser),
            Mock(NamedUser),
        ]
        response = GithubService(
            "", ORGANISATION_NAME).get_repository_collaborators("some-repo")
        self.assertEqual(2, len(response))

    def test_calls_downstream_services(self, _mock_github_client_core_api):
        github_service = GithubService("", ORGANISATION_NAME)
        github_service.get_repository_collaborators("test_repository")
        github_service.github_client_core_api.get_repo.assert_has_calls([
            call(TEST_REPOSITORY),
            call().get_collaborators('outside'),
            call().get_collaborators().__bool__(),
            call().get_collaborators().__iter__()
        ])

    def test_returns_empty_list_when_direct_users_returns_none(self, mock_github_client_core_api):
        mock_github_client_core_api.return_value.get_repo(
        ).get_collaborators.return_value = None
        self.assertEqual([], GithubService(
            "", ORGANISATION_NAME).get_repository_collaborators("test_repository"))

    def test_returns_exception_when_direct_users_returns_exception(self, mock_github_client_core_api):
        mock_github_client_core_api.return_value.get_repo(
        ).get_collaborators.side_effect = ConnectionError
        github_service = GithubService("", ORGANISATION_NAME)
        self.assertRaises(
            ConnectionError, github_service.get_repository_collaborators, "test_repository")


@patch("gql.transport.aiohttp.AIOHTTPTransport.__new__", new=MagicMock)
@patch("gql.Client.__new__", new=MagicMock)
@patch("github.Github.__new__")
class TestGithubServiceGetRepositoryDirectUsers(unittest.TestCase):

    def test_returns_direct_users(self, mock_github_client_core_api):
        mock_github_client_core_api.return_value.get_repo().get_collaborators.return_value = [
            Mock(NamedUser),
            Mock(NamedUser),
        ]
        response = GithubService(
            "", ORGANISATION_NAME).get_repository_direct_users("some-repo")
        self.assertEqual(2, len(response))

    def test_calls_downstream_services(self, _mock_github_client_core_api):
        github_service = GithubService("", ORGANISATION_NAME)
        github_service.get_repository_direct_users("test_repository")
        github_service.github_client_core_api.get_repo.assert_has_calls([
            call(TEST_REPOSITORY),
            call().get_collaborators('direct'),
            call().get_collaborators().__bool__(),
            call().get_collaborators().__iter__()
        ])

    def test_returns_empty_list_when_direct_users_returns_none(self, mock_github_client_core_api):
        mock_github_client_core_api.return_value.get_repo(
        ).get_collaborators.return_value = None
        self.assertEqual([], GithubService(
            "", ORGANISATION_NAME).get_repository_direct_users("test_repository"))

    def test_returns_exception_when_direct_users_returns_exception(self, mock_github_client_core_api):
        mock_github_client_core_api.return_value.get_repo(
        ).get_collaborators.side_effect = ConnectionError
        github_service = GithubService("", ORGANISATION_NAME)
        self.assertRaises(
            ConnectionError, github_service.get_repository_direct_users, "test_repository")


@patch("gql.transport.aiohttp.AIOHTTPTransport.__new__", new=MagicMock)
@patch("gql.Client.__new__")
@patch("github.Github.__new__", new=MagicMock)
class TestGithubServiceGetPaginatedListOfRepositoriesPerType(unittest.TestCase):
    def test_calls_downstream_services(self, _mock_gql_client):
        github_service = GithubService("", ORGANISATION_NAME)
        github_service.get_paginated_list_of_repositories_per_type(
            "public", "after_cursor")
        github_service.github_client_gql_api.execute.assert_called_once()

    def test_throws_value_error_when_page_size_greater_than_limit(self, _mock_gql_client):
        github_service = GithubService("", ORGANISATION_NAME)
        self.assertRaises(
            ValueError, github_service.get_paginated_list_of_repositories_per_type, "public", "test_after_cursor", 101)


@patch("gql.transport.aiohttp.AIOHTTPTransport.__new__", new=MagicMock)
@patch("gql.Client.__new__")
@patch("github.Github.__new__", new=MagicMock)
class TestGithubServiceGetPaginatedListOfRepositoriesPerTopic(unittest.TestCase):
    def test_calls_downstream_services(self, _mock_gql_client):
        github_service = GithubService("", ORGANISATION_NAME)
        github_service.get_paginated_list_of_repositories_per_topic(
            "standards-compliant", "after_cursor")
        github_service.github_client_gql_api.execute.assert_called_once()

    def test_throws_value_error_when_page_size_greater_than_limit(self, _mock_gql_client):
        github_service = GithubService("", ORGANISATION_NAME)
        self.assertRaises(
            ValueError, github_service.get_paginated_list_of_repositories_per_topic, "standards-compliant", "test_after_cursor", 101)


@patch("gql.transport.aiohttp.AIOHTTPTransport.__new__", new=MagicMock)
@patch("gql.Client.__new__", new=MagicMock)
@patch("github.Github.__new__", new=MagicMock)
class TestGithubServiceGetTeamRepositoryNames(unittest.TestCase):
    def setUp(self):
        self.return_data = {
            "organization": {
                "team": {
                    "repositories": {
                        "edges": [
                            {
                                "node": {
                                    "name": "test_repository",
                                },
                            },
                        ],
                        "pageInfo": {
                            "hasNextPage": False,
                            "endCursor": "test_end_cursor",
                        },
                    }
                }
            }
        }

    def test_returns_correct_data(self):
        github_service = GithubService("", ORGANISATION_NAME)
        github_service.get_paginated_list_of_team_repositories = MagicMock(
            return_value=self.return_data
        )
        repos = github_service.get_team_repository_names("some-team")
        self.assertEqual(len(repos), 1)
        self.assertEqual(repos[0], "test_repository")

    def test_nothing_to_return(self):
        github_service = GithubService("", ORGANISATION_NAME)
        self.return_data["organization"]["team"]["repositories"]["edges"] = None
        github_service.get_paginated_list_of_team_repositories = MagicMock(
            return_value=self.return_data
        )
        repos = github_service.get_team_repository_names("some-team")
        self.assertEqual(len(repos), 0)


@patch("gql.transport.aiohttp.AIOHTTPTransport.__new__", new=MagicMock)
@patch("gql.Client.__new__", new=MagicMock)
@patch("github.Github.__new__", new=MagicMock)
class TestGithubServiceGetTeamNames(unittest.TestCase):
    def setUp(self):
        self.return_data = {
            "organization": {
                "teams": {
                    "edges": [
                        {
                            "node": {
                                "slug": "test_team",
                            },
                        },
                    ],
                    "pageInfo": {
                        "hasNextPage": False,
                        "endCursor": "test_end_cursor",
                    },
                }
            }
        }

    def test_returns_correct_data(self):
        github_service = GithubService("", ORGANISATION_NAME)
        github_service.get_paginated_list_of_team_names = MagicMock(
            return_value=self.return_data
        )
        repos = github_service.get_team_names()
        self.assertEqual(len(repos), 1)
        self.assertEqual(repos[0], "test_team")

    def test_nothing_to_return(self):
        github_service = GithubService("", ORGANISATION_NAME)
        self.return_data["organization"]["teams"]["edges"] = None
        github_service.get_paginated_list_of_team_names = MagicMock(
            return_value=self.return_data
        )
        repos = github_service.get_team_names()
        self.assertEqual(len(repos), 0)


@patch("gql.transport.aiohttp.AIOHTTPTransport.__new__", new=MagicMock)
@patch("gql.Client.__new__", new=MagicMock)
@patch("github.Github.__new__", new=MagicMock)
class TestGithubServiceGetTeamUserNames(unittest.TestCase):
    def setUp(self):
        self.return_data = {
            "organization": {
                "team": {
                    "members": {
                        "edges": [
                            {
                                "node": {
                                    "login": "test_person",
                                },
                            },
                        ],
                        "pageInfo": {
                            "hasNextPage": False,
                            "endCursor": "test_end_cursor",
                        },
                    }
                }
            }
        }

    def test_returns_correct_data(self):
        github_service = GithubService("", ORGANISATION_NAME)
        github_service.get_paginated_list_of_team_user_names = MagicMock(
            return_value=self.return_data
        )
        repos = github_service.get_team_user_names("some-team")
        self.assertEqual(len(repos), 1)
        self.assertEqual(repos[0], "test_person")

    def test_nothing_to_return(self):
        github_service = GithubService("", ORGANISATION_NAME)
        self.return_data["organization"]["team"]["members"]["edges"] = None
        github_service.get_paginated_list_of_team_user_names = MagicMock(
            return_value=self.return_data
        )
        repos = github_service.get_team_user_names("some-team")
        self.assertEqual(len(repos), 0)


@patch("gql.transport.aiohttp.AIOHTTPTransport.__new__", new=MagicMock)
@patch("gql.Client.__new__", new=MagicMock)
@patch("github.Github.__new__", new=MagicMock)
class TestGithubServiceCheckCircleCIConfigInRepos(unittest.TestCase):
    def setUp(self):
        self.return_data = {
            "organization": {
                "repositories": {
                    "edges": [
                        {
                            "node": {
                                "name": "test_repository",
                                "object": {
                                    "id": "test_id"
                                }
                            },
                        },
                    ],
                    "pageInfo": {
                        "hasNextPage": False,
                        "endCursor": "test_end_cursor",
                    },
                }
            }
        }

    def test_returns_correct_data(self):
        github_service = GithubService("", ORGANISATION_NAME)
        github_service.get_paginated_circleci_config_check = MagicMock(
            return_value=self.return_data
        )
        repos = github_service.check_circleci_config_in_repos()
        self.assertEqual(len(repos), 1)
        self.assertEqual(repos[0], "test_repository")

    def test_no_circleci_config(self):
        github_service = GithubService("", ORGANISATION_NAME)
        self.return_data["organization"]["repositories"]["edges"][0]["node"]["object"] = None
        github_service.get_paginated_circleci_config_check = MagicMock(
            return_value=self.return_data
        )
        repos = github_service.check_circleci_config_in_repos()
        self.assertEqual(len(repos), 0)

    def test_nothing_to_return(self):
        github_service = GithubService("", ORGANISATION_NAME)
        self.return_data["organization"]["repositories"]["edges"] = None
        github_service.get_paginated_circleci_config_check = MagicMock(
            return_value=self.return_data
        )
        repos = github_service.check_circleci_config_in_repos()
        self.assertEqual(len(repos), 0)


@patch("gql.transport.aiohttp.AIOHTTPTransport.__new__", new=MagicMock)
@patch("gql.Client.__new__", new=MagicMock)
@patch("github.Github.__new__", new=MagicMock)
class TestGithubServiceGetPaginatedCircleCIConfigCheck(unittest.TestCase):
    def setUp(self):
        self.return_data = {
            "organization": {
                "repositories": {
                    "edges": [
                        {
                            "node": {
                                "name": "test_repository",
                                "object": {
                                    "id": "test_id"
                                }
                            },
                        },
                    ],
                    "pageInfo": {
                        "hasNextPage": False,
                        "endCursor": "test_end_cursor",
                    },
                }
            }
        }

    def test_returns_correct_data(self):
        github_service = GithubService("", ORGANISATION_NAME)
        github_service.github_client_gql_api.execute = MagicMock(
            return_value=self.return_data
        )
        result = github_service.get_paginated_circleci_config_check("test_cursor", 100)
        self.assertEqual(result, self.return_data)

    def test_page_size_too_large(self):
        github_service = GithubService("", ORGANISATION_NAME)
        with self.assertRaises(ValueError):
            github_service.get_paginated_circleci_config_check("test_cursor", github_service.GITHUB_GQL_MAX_PAGE_SIZE + 1)

    def test_returns_empty_data(self):
        github_service = GithubService("", ORGANISATION_NAME)
        github_service.github_client_gql_api.execute = MagicMock(
            return_value={}
        )
        result = github_service.get_paginated_circleci_config_check("test_cursor", 100)
        self.assertEqual(result, {})


@patch("gql.transport.aiohttp.AIOHTTPTransport.__new__", new=MagicMock)
@patch("gql.Client.__new__", new=MagicMock)
@patch("github.Github.__new__", new=MagicMock)
class TestGithubServiceGetOrgRepoNames(unittest.TestCase):
    def setUp(self):
        self.return_data = {
            "organization": {
                "repositories": {
                    "edges": [
                        {
                            "node": {
                                "name": "test_repository",
                                "isDisabled": False,
                            },
                        },
                    ],
                    "pageInfo": {
                        "hasNextPage": False,
                        "endCursor": "test_end_cursor",
                    },
                }
            }
        }

    def test_returns_correct_data(self):
        github_service = GithubService("", ORGANISATION_NAME)
        github_service.get_paginated_list_of_org_repository_names = MagicMock(
            return_value=self.return_data
        )
        repos = github_service.get_org_repo_names()
        self.assertEqual(len(repos), 1)
        self.assertEqual(repos[0], "test_repository")

    def test_returns_invalid_repository_type(self):
        github_service = GithubService("", ORGANISATION_NAME)

        self.return_data["organization"]["repositories"]["edges"][0]["node"]["isDisabled"] = True
        github_service.get_paginated_list_of_org_repository_names = MagicMock(
            return_value=self.return_data
        )
        repos = github_service.get_org_repo_names()
        self.assertEqual(len(repos), 0)
        self.return_data["organization"]["repositories"]["edges"][0]["node"]["isDisabled"] = False

    def test_nothing_to_return(self):
        github_service = GithubService("", ORGANISATION_NAME)
        self.return_data["organization"]["repositories"]["edges"] = None
        github_service.get_paginated_list_of_org_repository_names = MagicMock(
            return_value=self.return_data
        )
        repos = github_service.get_org_repo_names()
        self.assertEqual(len(repos), 0)


@patch("gql.transport.aiohttp.AIOHTTPTransport.__new__", new=MagicMock)
@patch("gql.Client.__new__", new=MagicMock)
@patch("github.Github.__new__", new=MagicMock)
class TestGithubServiceGetStaleOutsideCollaborators(unittest.TestCase):
    def setUp(self):
        self.return_data = {
            "organization": {
                "repositories": {
                    "pageInfo": {
                        "endCursor": "repo_1_end_cursor",
                        "hasNextPage": False
                    },
                    "nodes": [
                        {
                            "name": "repository_1",
                            "isDisabled": False,
                            "collaborators": {
                                "pageInfo": {
                                    "hasNextPage": False
                                },
                                "edges": [
                                    {
                                        "node": {
                                            "login": "outside_collab_1"
                                        }
                                    },
                                    {
                                        "node": {
                                            "login": "outside_collab_2"
                                        }
                                    },
                                ]
                            }
                        },
                        {
                            "name": "repository_2",
                            "isDisabled": False,
                            "collaborators": {
                                "pageInfo": {
                                    "hasNextPage": False
                                },
                                "edges": [
                                    {
                                        "node": {
                                            "login": "outside_collab_3"
                                        }
                                    },
                                ]
                            }
                        },
                    ]
                }
            }
        }
        self.all_outside_collaborators = [
            "outside_collab_1", "outside_collab_2", "outside_collab_3", "outside_collab_4"
        ]

    def test_returns_correct_data(self):
        github_service = GithubService("", ORGANISATION_NAME)
        github_service.get_paginated_list_of_unlocked_unarchived_repos_and_their_first_100_outside_collaborators = MagicMock(
            return_value=self.return_data
        )
        github_service.get_outside_collaborators_login_names = MagicMock(
            return_value=self.all_outside_collaborators
        )
        stale_outside_collaborators = github_service.get_stale_outside_collaborators()
        self.assertEqual(len(stale_outside_collaborators), 1)
        self.assertEqual(stale_outside_collaborators, ["outside_collab_4"])

    def test_counts_disabled_repo_outside_collaborators(self):
        github_service = GithubService("", ORGANISATION_NAME)
        self.return_data["organization"]["repositories"]["nodes"][1]["isDisabled"] = True
        github_service.get_paginated_list_of_unlocked_unarchived_repos_and_their_first_100_outside_collaborators = MagicMock(
            return_value=self.return_data
        )
        github_service.get_outside_collaborators_login_names = MagicMock(
            return_value=self.all_outside_collaborators
        )
        stale_outside_collaborators = github_service.get_stale_outside_collaborators()
        self.assertEqual(len(stale_outside_collaborators), 2)
        self.assertEqual(set(stale_outside_collaborators), set(["outside_collab_3", "outside_collab_4"]))

    def test_outside_collaborators_has_next_page_raises_error(self):
        github_service = GithubService("", ORGANISATION_NAME)
        self.return_data["organization"]["repositories"]["nodes"][1]["collaborators"]["pageInfo"]["hasNextPage"] = True
        github_service.get_paginated_list_of_unlocked_unarchived_repos_and_their_first_100_outside_collaborators = MagicMock(
            return_value=self.return_data
        )
        github_service.get_outside_collaborators_login_names = MagicMock(
            return_value=self.all_outside_collaborators
        )
        with self.assertRaises(ValueError):
            github_service.get_stale_outside_collaborators()


@patch("gql.transport.aiohttp.AIOHTTPTransport.__new__", new=MagicMock)
@patch("gql.Client.__new__", new=MagicMock)
@patch("github.Github.__new__", new=MagicMock)
class TestGithubServiceFetchAllRepositories(unittest.TestCase):
    def setUp(self):
        self.return_data = {
            "search": {
                "repos": [
                    {
                        "repo": {
                            "name": "test_repository",
                            "url": "test.com",
                            "isLocked": False,
                            "isDisabled": False,
                        },
                    },
                ],
                "pageInfo": {
                    "hasNextPage": False,
                    "endCursor": "test_end_cursor",
                },
            }
        }

    def test_returning_correct_data(self):
        github_service = GithubService("", ORGANISATION_NAME)
        github_service.get_paginated_list_of_repositories_per_type = MagicMock(
            return_value=self.return_data
        )
        repos = github_service.fetch_all_repositories_in_org()
        self.assertEqual(len(repos), 3)
        self.assertEqual(repos[0]["name"], "test_repository")
        self.assertFalse("unexpected_data" in repos[0])

    def test_nothing_to_return(self):
        github_service = GithubService("", ORGANISATION_NAME)
        self.return_data["search"]["repos"] = None
        github_service.get_paginated_list_of_repositories_per_type = MagicMock(
            return_value=self.return_data
        )
        repos = github_service.fetch_all_repositories_in_org()
        self.assertEqual(len(repos), 0)

    def test_ignore_locked_repo(self):
        github_service = GithubService("", ORGANISATION_NAME)
        self.return_data["search"]["repos"][0]["repo"]["isLocked"] = True
        github_service.get_paginated_list_of_repositories_per_type = MagicMock(
            return_value=self.return_data
        )
        repos = github_service.fetch_all_repositories_in_org()
        self.assertEqual(len(repos), 0)

    def test_ignore_disabled_repo(self):
        github_service = GithubService("", ORGANISATION_NAME)
        self.return_data["search"]["repos"][0]["repo"]["isDisabled"] = True
        github_service.get_paginated_list_of_repositories_per_type = MagicMock(
            return_value=self.return_data
        )
        repos = github_service.fetch_all_repositories_in_org()
        self.assertEqual(len(repos), 0)


@patch("gql.transport.aiohttp.AIOHTTPTransport.__new__", new=MagicMock)
@patch("gql.Client.__new__", new=MagicMock)
@patch("github.Github.__new__", new=MagicMock)
class TestGithubServiceGetMemberList(unittest.TestCase):
    def setUp(self):
        self.return_data_with_members = {
            "organization": {
                "membersWithRole": {
                    "nodes": [
                        {
                            "login": "test_user",
                            "organizationVerifiedDomainEmails": ["test_user@test.com"]
                        }
                    ],
                    "pageInfo": {
                        "hasNextPage": False,
                        "endCursor": "test_end_cursor",
                    },
                }
            }
        }

        self.return_data_no_members = {
            "organization": {
                "membersWithRole": {
                    "nodes": [],
                    "pageInfo": {
                        "hasNextPage": False,
                        "endCursor": "test_end_cursor",
                    },
                }
            }
        }

    def test_returns_correct_data(self):
        github_service = GithubService("", ORGANISATION_NAME)
        github_service._get_paginated_organization_members_with_emails = MagicMock(
            return_value=self.return_data_with_members
        )
        members = github_service.get_github_member_list()
        self.assertEqual(len(members), 1)
        self.assertEqual(members[0]["username"], "test_user")
        self.assertEqual(members[0]["email"], "test_user@test.com")

    def test_handles_no_members(self):
        github_service = GithubService("", ORGANISATION_NAME)
        github_service._get_paginated_organization_members_with_emails = MagicMock(
            return_value=self.return_data_no_members
        )
        members = github_service.get_github_member_list()
        self.assertEqual(len(members), 0)

    def test_handles_rate_limiting(self):
        github_service = GithubService("", ORGANISATION_NAME)
        github_service._get_paginated_organization_members_with_emails = MagicMock(
            side_effect=Exception("API rate limit exceeded")
        )
        with self.assertRaises(Exception) as context:
            github_service.get_github_member_list()
        self.assertIn('API rate limit exceeded', str(context.exception))

    def test_handles_pagination_as_expected(self):
        github_service = GithubService("", ORGANISATION_NAME)

        page_one = {
            "organization": {
                "membersWithRole": {
                    "nodes": [{"login": "test_user1", "organizationVerifiedDomainEmails": ["test_user1@test.com"]}],
                    "pageInfo": {"hasNextPage": True, "endCursor": "page2"},
                }
            }
        }

        page_two = {
            "organization": {
                "membersWithRole": {
                    "nodes": [{"login": "test_user2", "organizationVerifiedDomainEmails": ["test_user2@test.com"]}],
                    "pageInfo": {"hasNextPage": False, "endCursor": None},
                }
            }
        }

        github_service._get_paginated_organization_members_with_emails = MagicMock(
            side_effect=[page_one, page_two]
        )

        members = github_service.get_github_member_list()
        self.assertEqual(len(members), 2)
        self.assertEqual(members[0]["username"], "test_user1")
        self.assertEqual(members[1]["username"], "test_user2")


@patch("gql.transport.aiohttp.AIOHTTPTransport.__new__", new=MagicMock)
@patch("gql.Client.__new__")
@patch("github.Github.__new__", new=MagicMock)
class TestGithubServiceGetUserOrgEmailAddress(unittest.TestCase):
    def test_calls_downstream_services(self, _mock_gql_client):
        github_service = GithubService("", ORGANISATION_NAME)
        github_service.get_user_org_email_address("test_team_name")
        github_service.github_client_gql_api.assert_has_calls([
            call.execute().__getitem__('user'),
            call.execute().__getitem__().__getitem__('organizationVerifiedDomainEmails'),
            call.execute().__getitem__().__getitem__().__getitem__(0)
        ])

    def test_returns_email(self, mock_gql_client):
        mock_gql_client.return_value.execute.return_value = {
            "user": {"organizationVerifiedDomainEmails": ["test-email"]}}
        github_service = GithubService("", ORGANISATION_NAME)
        response = github_service.get_user_org_email_address("test_team_name")
        self.assertEqual(response, "test-email")

    def test_returns_default_value(self, mock_gql_client):
        mock_gql_client.return_value.execute.return_value = {
            "user": {"organizationVerifiedDomainEmails": []}}
        github_service = GithubService("", ORGANISATION_NAME)
        response = github_service.get_user_org_email_address("test_team_name")
        self.assertEqual(response, None)


@patch("gql.transport.aiohttp.AIOHTTPTransport.__new__", new=MagicMock)
@patch("gql.Client.__new__", new=MagicMock)
@patch("github.Github.__new__")
class TestGithubServiceGetOrgMembersLoginNames(unittest.TestCase):
    def test_calls_downstream_services(self, _mock_github_client_core_api):
        github_service = GithubService("", ORGANISATION_NAME)
        github_service.get_org_members_login_names()
        github_service.github_client_core_api.get_organization.assert_has_calls(
            [call(ORGANISATION_NAME), call().get_members(), call().get_members().__bool__(), call().get_members().__iter__()])

    def test_returns_login_names(self, mock_github_client_core_api):
        mock_github_client_core_api.return_value.get_organization().get_members.return_value = [
            Mock(NamedUser, login="tom-smith"),
            Mock(NamedUser, login="john.smith"),
        ]
        github_service = GithubService("", ORGANISATION_NAME)
        response = github_service.get_org_members_login_names()
        self.assertEqual(["tom-smith", "john.smith"], response)

    def test_returns_empty_list_when_members_returns_none(self, mock_github_client_core_api):
        mock_github_client_core_api.return_value.get_organization(
        ).get_members.return_value = None
        github_service = GithubService("", ORGANISATION_NAME)
        response = github_service.get_org_members_login_names()
        self.assertEqual([], response)


@patch("gql.transport.aiohttp.AIOHTTPTransport.__new__", new=MagicMock)
@patch("gql.Client.__new__", new=MagicMock)
@patch("github.Github.__new__", new=MagicMock)
@patch("requests.sessions.Session.__new__")
class TestGithubServiceGetUserFromAuditLog(unittest.TestCase):

    def test_calls_downstream_services(self, mock_github_client_rest_api):
        github_service = GithubService("", ORGANISATION_NAME)
        github_service.github_client_rest_api = mock_github_client_rest_api
        github_service._get_user_from_audit_log("some-user")
        mock_github_client_rest_api.assert_has_calls(
            [
                call.get(
                    'https://api.github.com/orgs/moj-analytical-services/audit-log?phrase=actor%3Asome-user', timeout=10),
                call.get().status_code.__eq__(200)
            ]
        )

    def test_returns_a_user(self, mock_github_client_rest_api):
        github_service = GithubService("", ORGANISATION_NAME)
        mock_github_client_rest_api.get().content = b"\"some-user\""
        mock_github_client_rest_api.get().status_code = 200
        github_service.github_client_rest_api = mock_github_client_rest_api
        user = github_service._get_user_from_audit_log("some-user")
        self.assertEqual(user, "some-user")

    def test_returns_zero_when_response_is_not_okay(self, mock_github_client_rest_api):
        github_service = GithubService("", ORGANISATION_NAME)
        mock_github_client_rest_api.get().status_code = 404
        github_service.github_client_rest_api = mock_github_client_rest_api
        response = github_service._get_user_from_audit_log("some-user")
        self.assertEqual(0, response)


@patch("gql.transport.aiohttp.AIOHTTPTransport.__new__", new=MagicMock)
@patch("gql.Client.__new__", new=MagicMock)
@patch("github.Github.__new__", new=MagicMock)
class TestDormantUser(unittest.TestCase):
    @patch.object(GithubService, 'is_user_dormant_since_date')
    def test_check_dormant_users_audit_activity_since_date(self, mock_is_user_dormant_since_date):
        # Set `is_user_dormant_since_date` to return `True` only for 'user2'
        mock_is_user_dormant_since_date.side_effect = lambda user, since_date: user == 'user2'
        github_service = GithubService("", ORGANISATION_NAME)
        result = github_service.check_dormant_users_audit_activity_since_date(
            ['user1', 'user2'], datetime.now() - timedelta(days=30))
        self.assertEqual(result, ['user2'])

    @patch.object(GithubService, 'enterprise_audit_activity_for_user')
    def test_is_user_dormant_since_date(self, mock_enterprise_audit_activity_for_user):
        # Set `enterprise_audit_activity_for_user` to return audit activity
        mock_enterprise_audit_activity_for_user.return_value = [
            {"@timestamp": (datetime.now() - timedelta(days=40)).timestamp() * 1000.0}]
        github_service = GithubService("", ORGANISATION_NAME)
        result = github_service.is_user_dormant_since_date(
            'user1', datetime.now() - timedelta(days=30))
        self.assertTrue(result)

    @patch.object(GithubService, 'enterprise_audit_activity_for_user')
    def test_is_user_not_dormant_since_date(self, mock_enterprise_audit_activity_for_user):
        # Set `enterprise_audit_activity_for_user` to return audit activity
        mock_enterprise_audit_activity_for_user.return_value = [
            {"@timestamp": (datetime.now() - timedelta(days=20)).timestamp() * 1000.0}]
        github_service = GithubService("", ORGANISATION_NAME)
        result = github_service.is_user_dormant_since_date(
            'user1', datetime.now() - timedelta(days=30))
        self.assertFalse(result)

    @patch.object(GithubService, 'enterprise_audit_activity_for_user')
    def test_is_user_dormant_no_audit_activity(self, mock_enterprise_audit_activity_for_user):
        # Set `enterprise_audit_activity_for_user` to return `None`
        mock_enterprise_audit_activity_for_user.return_value = None
        github_service = GithubService("", ORGANISATION_NAME)
        result = github_service.is_user_dormant_since_date(
            'user1', datetime.now() - timedelta(days=30))
        self.assertTrue(result)

    def test_enterprise_audit_log_is_checked(self):
        github_service = GithubService(
            "", ORGANISATION_NAME, enterprise_name=ENTERPRISE_NAME)

        mock_get = MagicMock()
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = b'"some-user"'
        github_service.github_client_rest_api.get = mock_get

        github_service.enterprise_audit_activity_for_user("some-user")

        expected_url = f"https://api.github.com/enterprises/{ENTERPRISE_NAME}/audit-log?phrase=actor%3Asome-user"
        mock_get.assert_called_once_with(expected_url, timeout=10)

    @patch('requests.get')
    def test_enterprise_audit_activity_for_user_failure(self, mock_get):
        # Mock `requests.get` to return a response with status code 404
        mock_get.return_value.status_code = 404
        github_service = GithubService("", ORGANISATION_NAME)
        with self.assertRaises(ValueError):
            github_service.enterprise_audit_activity_for_user('user1')


@patch("gql.transport.aiohttp.AIOHTTPTransport.__new__", new=MagicMock)
@patch("gql.Client.__new__", new=MagicMock)
@patch("github.Github.__new__", new=MagicMock)
@patch.object(GithubService, "_get_user_from_audit_log")
class TestGithubServiceGetAuditLogActiveUsers(unittest.TestCase):

    def test_get_audit_log_active_users_when_no_users_passed_in(self, mock_get_user_from_audit_log):
        github_service = GithubService("", ORGANISATION_NAME)
        response = github_service.get_audit_log_active_users([])
        self.assertEqual(0, len(response))
        mock_get_user_from_audit_log.assert_not_called()

    def test_get_audit_log_active_users_when_no_user_data_from_audit_log(self, mock_get_user_from_audit_log):
        github_service = GithubService("", ORGANISATION_NAME)
        users = [
            {
                "username": "some-user",
                "is_outside_collaborator": False,
            }
        ]
        mock_get_user_from_audit_log.return_value = []
        response = github_service.get_audit_log_active_users(users)
        self.assertEqual(0, len(response))

    def test_get_audit_log_active_users_when_user_not_active(self, mock_get_user_from_audit_log):
        github_service = GithubService("", ORGANISATION_NAME)
        users = [
            {
                "username": "some-user",
                "is_outside_collaborator": False,
            }
        ]
        mock_get_user_from_audit_log.return_value = [
            {"@timestamp": 1080866000003}
        ]
        response = github_service.get_audit_log_active_users(users)
        self.assertEqual(0, len(response))

    def test_get_audit_log_active_users_when_user_is_active(self, mock_get_user_from_audit_log):
        github_service = GithubService("", ORGANISATION_NAME)
        users = [
            {
                "username": "some-user",
                "is_outside_collaborator": False,
            }
        ]
        current_time = datetime.now(timezone.utc)
        unix_timestamp = current_time.timestamp() * 1000
        mock_get_user_from_audit_log.return_value = [
            {"@timestamp": unix_timestamp}
        ]
        response = github_service.get_audit_log_active_users(users)
        self.assertEqual(1, len(response))


@patch("gql.transport.aiohttp.AIOHTTPTransport.__new__", new=MagicMock)
@patch("gql.Client.__new__", new=MagicMock)
@patch("github.Github.__new__")
class TestGithubServiceRemoveUserFromGitHub(unittest.TestCase):
    def test_remove_user_from_gitub(self, mock_github_client_core_api):
        mock_github_client_core_api.return_value.get_user.return_value = "mock-user"
        github_service = GithubService("", ORGANISATION_NAME)
        github_service.remove_user_from_gitub("some-user")
        github_service.github_client_core_api.get_user.assert_has_calls(
            [call('some-user')]
        )
        github_service.github_client_core_api.get_organization.assert_has_calls(
            [
                call(ORGANISATION_NAME),
                call().remove_from_membership("mock-user"),
            ]
        )


class MockGithubIssue(MagicMock):
    def __init__(self, the_id, number, title, assignees, _label):
        mock_label = MagicMock(name="test_support_label")
        super().__init__()
        self.id = the_id
        self.number = number
        self.title = title
        self.assignees = assignees
        self.labels = [mock_label]
        self.user = MagicMock()

    def edit(self, assignees):
        self.assignees = assignees


@patch("gql.transport.aiohttp.AIOHTTPTransport.__new__", new=MagicMock)
@patch("gql.Client.__new__", new=MagicMock)
class TestReturningLicences(unittest.TestCase):

    @patch("services.github_service.Github")
    def test_get_remaining_licences(self, mock_github):
        org_token = 'dummy_token'
        org_name = 'dummy_org'
        enterprise_name = 'ministry-of-justice-uk'
        service = GithubService(org_token, org_name, enterprise_name)

        mock_enterprise = MagicMock()
        mock_licenses = MagicMock()
        mock_licenses.total_seats_purchased = 100
        mock_licenses.total_seats_consumed = 50

        mock_github.return_value.get_enterprise.return_value = mock_enterprise
        mock_enterprise.get_consumed_licenses.return_value = mock_licenses

        remaining_licenses = service.get_remaining_licences()

        self.assertEqual(remaining_licenses, 50)


@patch("gql.transport.aiohttp.AIOHTTPTransport.__new__", new=MagicMock)
@patch("gql.Client.__new__", new=MagicMock)
@patch("services.github_service.Github")
class TestReportOnInactiveUsers(unittest.TestCase):

    def setUp(self) -> None:
        self.team = Mock()
        self.commit = Mock()
        self.team.name = "team1"
        self.team.id = 1

        self.user1 = Mock()
        self.user1.login = "user1"
        self.user2 = Mock()
        self.user2.login = "user2"

        self.repository1 = Mock()
        self.repository1.name = "repo1"
        self.repository2 = Mock()
        self.repository2.name = "repo2"

        self.users = [self.user1, self.user2]
        self.repositories = [self.repository1, self.repository2]
        self.ignored_users = ["user2"]
        self.ignored_repositories = ["repo2"]

        self.inactivity_months = 18

    def test_identify_inactive_users_in_a_team(self, _mock_github_client_core_api):

        github_service = GithubService("", ORGANISATION_NAME)
        github_service._get_repositories_managed_by_team = Mock(
            return_value=self.repositories)
        github_service._get_unignored_users_from_team = Mock(
            return_value=self.users)

        inactive_users = github_service.get_inactive_users(
            self.team.id, self.ignored_users, self.ignored_repositories, self.inactivity_months)

        self.assertEqual(2, len(inactive_users))
        self.assertEqual("user1", inactive_users[0].login)

    def test_identify_no_inactive_users_in_a_team(self, _mock_github_client_core_api):
        self.commit = Mock()
        self.commit.commit.author.date = datetime.now()
        self.repository1.get_commits.return_value = [self.commit]

        github_service = GithubService("", ORGANISATION_NAME)
        github_service._get_repositories_managed_by_team = Mock(
            return_value=self.repositories)
        github_service._get_unignored_users_from_team = Mock(
            return_value=self.users)

        inactive_users = github_service.get_inactive_users(
            self.team.id, self.ignored_users, self.ignored_repositories, self.inactivity_months)

        self.assertEqual(0, len(inactive_users))

    def test_identify_inactive_users(self, _mock_github_client_core_api):

        github_service = GithubService("", ORGANISATION_NAME)

        github_service._is_user_inactive = Mock(return_value=True)

        inactive_users = github_service._identify_inactive_users(
            self.users, self.repositories, self.inactivity_months)

        self.assertEqual(2, len(inactive_users))
        self.assertEqual("user1", inactive_users[0].login)

    def test_get_users_from_team_found(self, mock_github_client_core_api):

        mock_github_client_core_api.return_value.get_organization().get_members.return_value = [
            self.user1, self.user2
        ]
        mock_team = mock_github_client_core_api.return_value.get_organization().get_team()
        mock_team.get_members.return_value = [
            self.user1, self.user2
        ]
        mock_github_client_core_api.return_value.get_user.side_effect = [
            self.user1, self.user2
        ]

        github_service = GithubService(
            org_token="test_token", organisation_name="test_org")

        result = github_service._get_unignored_users_from_team(
            self.team.id, self.ignored_users)

        self.assertEqual(1, len(result))

    def test_user_is_inactive(self, _mock_github_client_core_api):

        self.commit = Mock()
        self.commit.commit.author.date = datetime.now(
        ) - timedelta(days=self.inactivity_months * 30)

        self.repository1.get_commits.return_value = [self.commit]

        github_service = GithubService("", ORGANISATION_NAME)

        result = github_service._is_user_inactive(
            self.user1, self.repositories, self.inactivity_months)

        self.assertEqual(True, result)

    def test_user_is_active(self, _mock_github_client_core_api):

        self.commit = Mock()
        self.commit.commit.author.date = datetime.now()

        self.repository1.get_commits.return_value = [self.commit]

        github_service = GithubService("", ORGANISATION_NAME)

        result = github_service._is_user_inactive(
            self.user1, self.repositories, self.inactivity_months)

        self.assertEqual(False, result)

    def test_user_is_inactive_no_commits(self, mock_github_client_core_api):

        mock_github_client_core_api.return_value.get_organization().get_members.return_value = [
            self.user1, self.user2
        ]
        mock_team = mock_github_client_core_api.return_value.get_organization().get_team()
        mock_team.get_members.return_value = [
            self.user1, self.user2
        ]
        mock_github_client_core_api.return_value.get_user.side_effect = [
            self.user1, self.user2
        ]
        mock_github_client_core_api.return_value.get_organization().get_repos.return_value = [
            self.repository1, self.repository2
        ]
        mock_github_client_core_api.return_value.get_organization().Repository.get_commits.side_effect = [
            GithubException(status=500, data="test", headers={})
        ]

        github_service = GithubService("", ORGANISATION_NAME)

        with self.assertLogs(level='ERROR') as cm:
            github_service._is_user_inactive(
                self.user1, self.repositories, self.inactivity_months)
            self.assertEqual(
                "ERROR:root:An exception occurred while getting commit date for user user1 in repo repo1", cm.output[0])

    def test_get_all_repositories_managed_by_team(self, mock_github_client_core_api):
        mock_github_client_core_api.return_value.get_organization().get_team().get_repos.return_value = [
            self.repository1, self.repository2
        ]

        github_service = GithubService("", ORGANISATION_NAME)

        result = github_service._get_repositories_managed_by_team(
            self.team.id, self.ignored_repositories)

        self.assertEqual(1, len(result))

    def test_get_all_repositories_managed_by_team_are_ignored(self, mock_github_client_core_api):
        mock_github_client_core_api.return_value.get_organization().get_team().get_repos.return_value = [
            self.repository2
        ]

        github_service = GithubService("", ORGANISATION_NAME)

        result = github_service._get_repositories_managed_by_team(
            self.team.id, self.ignored_repositories)

        self.assertEqual(0, len(result))


@patch("gql.transport.aiohttp.AIOHTTPTransport.__new__", new=MagicMock)
@patch("gql.Client.__new__", new=MagicMock)
@patch("github.Github.__new__")
class TestSetStandards(unittest.TestCase):
    def test_set_standards(self, mock_github_client_core_api: MagicMock):
        mock_protection = Mock(required_status_checks=Mock(
            contexts=["test"], strict=True))
        mock_branch = Mock(Branch)
        mock_branch.get_protection.return_value = mock_protection
        mock_repo = MagicMock(Repository)
        mock_repo.get_branch.return_value = mock_branch
        mock_github_client_core_api.return_value.get_repo.return_value = mock_repo

        github_service = GithubService("", ORGANISATION_NAME)
        github_service.set_standards("test_repository")

        mock_branch.edit_protection.assert_called_with(contexts=["test"],
                                                       strict=True,
                                                       enforce_admins=True,
                                                       required_approving_review_count=1,
                                                       dismiss_stale_reviews=True, )

    def test_set_standards_handles_null_required_checks(self, mock_github_client_core_api: MagicMock):
        mock_protection = Mock(required_status_checks=None)
        mock_branch = Mock(Branch)
        mock_branch.get_protection.return_value = mock_protection
        mock_repo = MagicMock(Repository)
        mock_repo.get_branch.return_value = mock_branch
        mock_github_client_core_api.return_value.get_repo.return_value = mock_repo

        github_service = GithubService("", ORGANISATION_NAME)
        github_service.set_standards("test_repository")

        mock_branch.edit_protection.assert_called_with(contexts=[],
                                                       strict=False,
                                                       enforce_admins=True,
                                                       required_approving_review_count=1,
                                                       dismiss_stale_reviews=True, )


@patch("gql.transport.aiohttp.AIOHTTPTransport.__new__", new=MagicMock)
@patch("gql.Client.__new__", new=MagicMock)
@patch("github.Github.__new__")
class TestGithubServiceUpdateTeamRepositoryPermission(unittest.TestCase):

    def test_updates_team_repository_permission(self, mock_github_client_core_api):
        mock_team = MagicMock()
        mock_repo1 = MagicMock()
        mock_repo2 = MagicMock()
        mock_org = MagicMock()
        mock_org.get_team_by_slug.return_value = mock_team
        mock_org.get_repo.side_effect = [mock_repo1, mock_repo2]
        mock_github_client_core_api.return_value.get_organization.return_value = mock_org

        repositories = ["repo1", "repo2"]
        github_service = GithubService("", ORGANISATION_NAME)
        github_service.update_team_repository_permission(
            "dev-team", repositories, "write")

        mock_github_client_core_api.return_value.get_organization.assert_called_once_with(
            ORGANISATION_NAME)
        mock_org.get_team_by_slug.assert_called_once_with("dev-team")
        mock_org.get_repo.assert_has_calls([call("repo1"), call("repo2")])
        mock_team.set_repo_permission.assert_has_calls(
            [call(mock_repo1, "write"), call(mock_repo2, "write")])

    def test_raises_error_for_nonexistent_team(self, mock_github_client_core_api):
        mock_org = MagicMock()
        mock_org.get_team_by_slug.side_effect = UnknownObjectException(
            404, "Team not found")
        mock_github_client_core_api.return_value.get_organization.return_value = mock_org

        github_service = GithubService("", ORGANISATION_NAME)
        with self.assertRaises(ValueError):
            github_service.update_team_repository_permission(
                "unknown-team", ["repo1"], "write")

    def test_raises_error_for_nonexistent_repository(self, mock_github_client_core_api):
        mock_team = MagicMock()
        mock_org = MagicMock()
        mock_org.get_team_by_slug.return_value = mock_team
        mock_org.get_repo.side_effect = UnknownObjectException(
            404, "Repository not found")
        mock_github_client_core_api.return_value.get_organization.return_value = mock_org

        github_service = GithubService("", ORGANISATION_NAME)
        with self.assertRaises(ValueError):
            github_service.update_team_repository_permission(
                "dev-team", ["unknown-repo"], "write")


@patch("gql.transport.aiohttp.AIOHTTPTransport.__new__", new=MagicMock)
@patch("gql.Client.__new__", new=MagicMock)
@patch("services.github_service.Github")
class TestNewOwnerDetected(unittest.TestCase):

    def test_flag_owner_permission_changes(self, _mock_github_client_core_api):
        github_service = GithubService("", ORGANISATION_NAME)
        mock_audit_log = [
            {'action': 'org.add_member', 'createdAt': '2023-12-06T10:32:07.832Z', 'actorLogin': 'testAdmin',
             'operationType': 'CREATE', 'permission': 'READ', 'userLogin': 'testUser'},
            {'action': 'org.add_member', 'createdAt': '2023-12-06T10:33:07.832Z', 'actorLogin': 'johnsmith',
             'operationType': 'CREATE', 'permission': 'ADMIN', 'userLogin': 'janedoe'}
        ]
        github_service.audit_log_member_changes = Mock(
            return_value=mock_audit_log)

        result = github_service.flag_owner_permission_changes("2023-12-01")

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['action'], 'org.add_member')
        self.assertEqual(result[0]['permission'], 'ADMIN')
        self.assertEqual(result[0]['userLogin'], 'janedoe')

    def test_audit_log_member_changes(self, _mock_github_client_gql):
        github_service = GithubService("", ORGANISATION_NAME)
        return_value = {
            "organization": {
                "auditLog": {
                    "edges": [
                        {"node": {"action": "org.add_member", "createdAt": "2023-12-06T10:32:07.832Z",
                                  "actorLogin": "user1", "permission": "READ"}},
                        {"node": {"action": "org.update_member", "createdAt": "2023-12-06T10:33:07.832Z",
                                  "actorLogin": "user2", "permission": "ADMIN"}}
                    ],
                    "pageInfo": {
                        "endCursor": None,
                        "hasNextPage": False
                    }
                }
            }
        }

        github_service.github_client_gql_api.execute.return_value = return_value

        result = github_service.audit_log_member_changes("2023-12-01")

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['action'], 'org.add_member')
        self.assertEqual(result[0]['permission'], 'READ')

    def test_check_for_audit_log_new_members(self, _mock_github_client_gql):
        github_service = GithubService("", ORGANISATION_NAME)
        return_value = {
            "organization": {
                "auditLog": {
                    "edges": [
                        {"node": {"action": "org.add_member", "createdAt": "2023-12-06T10:32:07.832Z",
                                            "actorLogin": "user1", "userLogin": "new_member1"}},
                        {"node": {"action": "org.add_member", "createdAt": "2023-12-07T11:32:07.832Z",
                                            "actorLogin": "user2", "userLogin": "new_member2"}}
                    ],
                    "pageInfo": {
                        "endCursor": None,
                        "hasNextPage": False
                    }
                }
            }
        }

        github_service.github_client_gql_api.execute.return_value = return_value

        result = github_service.check_for_audit_log_new_members("2023-12-01")

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['action'], 'org.add_member')
        self.assertEqual(result[0]['actorLogin'], 'user1')
        self.assertEqual(result[0]['userLogin'], 'new_member1')

        self.assertEqual(result[1]['action'], 'org.add_member')
        self.assertEqual(result[1]['actorLogin'], 'user2')
        self.assertEqual(result[1]['userLogin'], 'new_member2')


@patch("gql.transport.aiohttp.AIOHTTPTransport.__new__", new=MagicMock)
@patch("gql.Client.__new__", new=MagicMock)
@patch("github.Github.__new__")
@patch("requests.sessions.Session.__new__")
class TestGHAMinutesQuotaOperations(unittest.TestCase):

    def test_get_all_organisations_in_enterprise(self, _mock_github_client_rest_api, mock_github_client_core_api):
        mock_github_client_core_api.return_value.get_user().get_orgs.return_value = [
            Mock(Organization, login="org1"),
            Mock(Organization, login="org2"),
        ]

        response = GithubService(
            "", ORGANISATION_NAME).get_all_organisations_in_enterprise()

        self.assertEqual(["org1", "org2"], response)

    def test_get_gha_minutes_used_for_organisation(self, mock_github_client_rest_api, _mock_github_client_core_api):
        github_service = GithubService("", ORGANISATION_NAME)
        github_service.github_client_rest_api = mock_github_client_rest_api
        github_service.get_gha_minutes_used_for_organisation("org1")
        mock_github_client_rest_api.assert_has_calls(
            [
                call.get('https://api.github.com/orgs/org1/settings/billing/actions', headers={
                         'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'})
            ]
        )

    def test_modify_gha_minutes_quota_threshold(self, mock_github_client_rest_api, _mock_github_client_core_api):
        github_service = GithubService("", ORGANISATION_NAME)
        github_service.github_client_rest_api = mock_github_client_rest_api
        github_service.modify_gha_minutes_quota_threshold(80)
        mock_github_client_rest_api.assert_has_calls(
            [
                call.patch('https://api.github.com/repos/ministryofjustice/operations-engineering/actions/variables/GHA_MINUTES_QUOTA_THRESHOLD',
                           '{"value": "80"}', headers={'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'})
            ]
        )

    def test_get_repository_variable(self, _mock_github_client_rest_api, mock_github_client_core_api):
        mock_github_client_core_api.return_value.get_repo().get_variable.return_value = Mock(
            Variable, name="GHA_MINUTES_QUOTA_THRESHOLD", value="70")

        response = GithubService(
            "", ORGANISATION_NAME)._get_repository_variable(variable_name="GHA_MINUTES_QUOTA_THRESHOLD")

        self.assertEqual('70', response)

    @freeze_time("2021-02-01")
    @patch.object(GithubService, "_get_repository_variable")
    @patch.object(GithubService, "modify_gha_minutes_quota_threshold")
    def test_reset_alerting_threshold_if_first_day_of_month(
        self,
        mock_modify_gha_minutes_quota_threshold,
        mock_get_repository_variable,
        _mock_github_client_rest_api,
        _mock_github_client_core_api
    ):
        github_service = GithubService("", ORGANISATION_NAME)

        mock_get_repository_variable.side_effect = self._mock_repository_variable

        github_service.reset_alerting_threshold_if_first_day_of_month()

        mock_modify_gha_minutes_quota_threshold.assert_called_once_with(70)

    @freeze_time("2021-02-22")
    @patch.object(GithubService, "_get_repository_variable")
    @patch.object(GithubService, "modify_gha_minutes_quota_threshold")
    def test_reset_alerting_threshold_if_not_first_day_of_month(
        self,
        mock_modify_gha_minutes_quota_threshold,
        mock_get_repository_variable,
        _mock_github_client_rest_api,
        _mock_github_client_core_api
    ):

        github_service = GithubService("", ORGANISATION_NAME)

        mock_get_repository_variable.side_effect = self._mock_repository_variable

        github_service.reset_alerting_threshold_if_first_day_of_month()

        assert not mock_modify_gha_minutes_quota_threshold.called

    @patch.object(GithubService, "get_gha_minutes_used_for_organisation")
    def test_calculate_total_minutes_used(self, mock_get_gha_minutes_used_for_organisation, _mock_github_client_rest_api, _mock_github_client_core_api):
        github_service = GithubService("", ORGANISATION_NAME)

        mock_get_gha_minutes_used_for_organisation.return_value = {
            "total_minutes_used": 10}

        self.assertEqual(
            github_service.calculate_total_minutes_used(["org1", "org2"]), 20)

    @patch.object(GithubService, "_get_repository_variable")
    @patch.object(GithubService, "reset_alerting_threshold_if_first_day_of_month")
    @patch.object(GithubService, "calculate_total_minutes_used")
    @patch.object(GithubService, "get_all_organisations_in_enterprise")
    def test_alert_on_low_quota_if_low(
        self,
        mock_get_all_organisations_in_enterprise,
        mock_calculate_total_minutes_used,
        mock_reset_alerting_threshold_if_first_day_of_month,
        mock_get_repository_variable,
        _mock_github_client_rest_api,
        _mock_github_client_core_api
    ):
        github_service = GithubService("", ORGANISATION_NAME)

        mock_get_all_organisations_in_enterprise.return_value = [
            "org1", "org2"]
        mock_calculate_total_minutes_used.return_value = 37500
        mock_get_repository_variable.side_effect = self._mock_repository_variable

        result = github_service.check_if_gha_minutes_quota_is_low()

        mock_reset_alerting_threshold_if_first_day_of_month.assert_called_once()
        self.assertEqual(result['threshold'], 70)
        self.assertEqual(result['percentage_used'], 75)

    @patch.object(GithubService, "_get_repository_variable")
    @patch.object(GithubService, "reset_alerting_threshold_if_first_day_of_month")
    @patch.object(GithubService, "calculate_total_minutes_used")
    @patch.object(GithubService, "get_all_organisations_in_enterprise")
    def test_alert_on_low_quota_if_not_low(
        self,
        mock_get_all_organisations_in_enterprise,
        mock_calculate_total_minutes_used,
        mock_reset_alerting_threshold_if_first_day_of_month,
        mock_get_repository_variable,
        _mock_github_client_rest_api,
        _mock_github_client_core_api
    ):
        github_service = GithubService("", ORGANISATION_NAME)

        mock_get_all_organisations_in_enterprise.return_value = [
            "org1", "org2"]
        mock_calculate_total_minutes_used.return_value = 5000
        mock_get_repository_variable.side_effect = self._mock_repository_variable

        result = github_service.check_if_gha_minutes_quota_is_low()

        mock_reset_alerting_threshold_if_first_day_of_month.assert_called_once()
        self.assertEqual(result, False)

    def _mock_repository_variable(self, name):
        return {
            "GHA_MINUTES_QUOTA_TOTAL": "50000",
            "GHA_MINUTES_QUOTA_THRESHOLD": "70",
            "GHA_MINUTES_QUOTA_BASE_THRESHOLD": "70"
        }.get(name)


@patch("gql.transport.aiohttp.AIOHTTPTransport.__new__", new=MagicMock)
@patch("gql.Client.__new__", new=MagicMock)
@patch("github.Github.__new__")
@patch("requests.sessions.Session.__new__")
class TestGithubServicePATRetrieval(unittest.TestCase):

    @patch.object(GithubService, "get_new_pat_creation_events_for_organization")
    def test_successful_pat_retrieval(self, mock_get_new_pat_creation_events, _mock_github_client_rest_api, _mock_github_client_core_api):
        expected_response = [{
            "id": 25381,
            "token_expired": False,
            "owner": {"login": "test_owner"}
        }]
        mock_get_new_pat_creation_events.return_value = expected_response

        github_service = GithubService("test_token", "test_org")
        result = github_service.get_new_pat_creation_events_for_organization()

        self.assertEqual(result, expected_response)
        mock_get_new_pat_creation_events.assert_called_once()


@patch("gql.transport.aiohttp.AIOHTTPTransport.__new__", new=MagicMock)
@patch("gql.Client.__new__", new=MagicMock)
@patch("github.Github.__new__")
class TestGithubServiceGetAllEnterpriseMembers(unittest.TestCase):

    def test_get_all_enterprise_members(self, mock_github_client_core_api):
        mock_github_client_core_api.return_value.get_organization().get_members.return_value = [
            Mock(NamedUser),
            Mock(NamedUser),
        ]
        response = GithubService("", ORGANISATION_NAME).get_all_enterprise_members()
        self.assertEqual(2, len(response))


@patch("gql.transport.aiohttp.AIOHTTPTransport.__new__", new=MagicMock)
@patch("gql.Client.__new__", new=MagicMock)
@patch("github.Github.__new__")
class TestGetOldPOCRepositories(unittest.TestCase):

    @freeze_time("2024-10-24")
    def test_calculate_repo_age(self, mock_github_client_core_api):
        mock_github_client_core_api.return_value.get_repo().created_at = datetime.fromisoformat("2024-10-04 00:00:00+00:00")

        response = GithubService("", ORGANISATION_NAME).calculate_repo_age("repo1")

        self.assertEqual(20, response)

    @patch.object(GithubService, "calculate_repo_age")
    @patch.object(GithubService, "get_paginated_list_of_repositories_per_topic")
    def test_get_old_poc_repositories_if_exist(self, mock_get_paginated_list_of_repositories_per_topic, mock_calculate_repo_age, _mock_github_client_core_api):
        mock_get_paginated_list_of_repositories_per_topic.return_value = {'search': {'repos': [{'repo': {'name': 'operations-engineering-metadata-poc', 'isDisabled': False, 'isLocked': False, 'hasIssuesEnabled': True, 'repositoryTopics': {'edges': [{'node': {'topic': {'name': 'operations-engineering'}}}, {'node': {'topic': {'name': 'poc'}}}]}, 'collaborators': {'totalCount': 0}}}, {'repo': {'name': 'operations-engineering-unit-test-generator-poc', 'isDisabled': False, 'isLocked': False, 'hasIssuesEnabled': True, 'repositoryTopics': {'edges': [{'node': {'topic': {'name': 'operations-engineering'}}}, {'node': {'topic': {'name': 'poc'}}}]}, 'collaborators': {'totalCount': 0}}},], 'pageInfo': {'hasNextPage': False, 'endCursor': 'Y3Vyc29yOjQ='}}}
        mock_calculate_repo_age.return_value = 30

        response = GithubService("", ORGANISATION_NAME).get_old_poc_repositories()

        self.assertEqual({"operations-engineering-metadata-poc": 30, "operations-engineering-unit-test-generator-poc": 30}, response)

    @patch.object(GithubService, "get_paginated_list_of_repositories_per_topic")
    def test_get_old_poc_repositories_if_not_exist(self, mock_get_paginated_list_of_repositories_per_topic, _mock_github_client_core_api):
        mock_get_paginated_list_of_repositories_per_topic.return_value = {'search': {'repos': [], 'pageInfo': {'hasNextPage': False, 'endCursor': 'Y3Vyc29yOjQ='}}}

        response = GithubService("", ORGANISATION_NAME).get_old_poc_repositories()

        self.assertEqual({}, response)


@patch("gql.transport.aiohttp.AIOHTTPTransport.__new__", new=MagicMock)
@patch("gql.Client.__new__", new=MagicMock)
@patch("services.github_service.Github")
class TestUserRemovalEvents(unittest.TestCase):
    def test_get_user_removal_events(self, _mock_github_client_gql):
        github_service = GithubService("", ORGANISATION_NAME)
        return_value = {
            "organization": {
                "auditLog": {
                    "edges": [
                        {"node": {"action": "org.remove_member", "createdAt": "2023-12-06T10:32:07.832Z",
                                            "actorLogin": "admin_user", "userLogin": "removed_user1"}},
                        {"node": {"action": "org.remove_member", "createdAt": "2023-12-07T11:32:07.832Z",
                                            "actorLogin": "admin_user", "userLogin": "removed_user2"}}
                    ],
                    "pageInfo": {
                        "endCursor": None,
                        "hasNextPage": False
                    }
                }
            }
        }

        github_service.github_client_gql_api.execute.return_value = return_value

        result = github_service.get_user_removal_events("2023-12-01", "admin_user")

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['action'], 'org.remove_member')
        self.assertEqual(result[0]['actorLogin'], 'admin_user')
        self.assertEqual(result[0]['userLogin'], 'removed_user1')

        self.assertEqual(result[1]['action'], 'org.remove_member')
        self.assertEqual(result[1]['actorLogin'], 'admin_user')
        self.assertEqual(result[1]['userLogin'], 'removed_user2')





@patch("gql.transport.aiohttp.AIOHTTPTransport.__new__", new=MagicMock)
@patch("gql.Client.__new__", new=MagicMock)
@patch("github.Github.__new__")
class TestGithubServiceGetCurrentContributorsForActiveRepos(unittest.TestCase):
    def setUp(self):
        self.active_repos = ["repo1", "repo2", "repo3"]

    def test_drops_non_member_contributors(
            self,
            mock_github_client_core_api
        ):
        github_service = GithubService("", ORGANISATION_NAME)
        github_service.get_active_repositories = MagicMock(return_value=self.active_repos)

        mock_github_client_core_api.return_value.get_organization.return_value.get_members.return_value = [
            Mock(NamedUser, login="c1"),
            Mock(NamedUser, login="c2")
        ]

        mock_github_client_core_api.return_value.get_repo.side_effect = [
            MagicMock(get_contributors=MagicMock(return_value=[MagicMock(login="c1"), MagicMock(login="c2"), MagicMock(login="c3")])),
            MagicMock(get_contributors=MagicMock(return_value=[MagicMock(login="c2"), MagicMock(login="c4")])),
            MagicMock(get_contributors=MagicMock(return_value=[MagicMock(login="c3"), MagicMock(login="c1")]))
        ]
        response = github_service.get_current_contributors_for_active_repos()
        expected = [{'repository': 'repo1', 'contributors': {'c1', 'c2'}}, {'repository': 'repo2', 'contributors': {'c2'}}, {'repository': 'repo3', 'contributors': {'c1'}}]
        self.assertEqual(response, expected)

    def test_returns_sorted_by_number_of_contributors_descending(
            self,
            mock_github_client_core_api
        ):
        github_service = GithubService("", ORGANISATION_NAME)
        github_service.get_active_repositories = MagicMock(
            return_value=self.active_repos
        )

        mock_github_client_core_api.return_value.get_organization.return_value.get_members.return_value = [
            Mock(NamedUser, login="c1"),
            Mock(NamedUser, login="c2")
        ]

        mock_github_client_core_api.return_value.get_repo.side_effect = [
            MagicMock(get_contributors=MagicMock(return_value=[MagicMock(login="c1"), MagicMock(login="c3")])),
            MagicMock(get_contributors=MagicMock(return_value=[MagicMock(login="c2"), MagicMock(login="c1")])),
            MagicMock(get_contributors=MagicMock(return_value=[MagicMock(login="c3")]))
        ]
        response = github_service.get_current_contributors_for_active_repos()
        expected = [{'repository': 'repo2', 'contributors': {'c1', 'c2'}}, {'repository': 'repo1', 'contributors': {'c1'}}]
        self.assertEqual(response, expected)

    def test_drops_repos_with_zero_contributors(
            self,
            mock_github_client_core_api
        ):
        github_service = GithubService("", ORGANISATION_NAME)
        github_service.get_active_repositories = MagicMock(
            return_value=self.active_repos
        )

        mock_github_client_core_api.return_value.get_organization.return_value.get_members.return_value = [
            Mock(NamedUser, login="c1"),
            Mock(NamedUser, login="c2")
        ]

        mock_github_client_core_api.return_value.get_repo.side_effect = [
            MagicMock(get_contributors=MagicMock(return_value=[MagicMock(login="c1"), MagicMock(login="c3")])),
            MagicMock(get_contributors=MagicMock(return_value=[MagicMock(login="c3"), MagicMock(login="c4")])),
            MagicMock(get_contributors=MagicMock(return_value=[MagicMock(login=None)]))
        ]
        response = github_service.get_current_contributors_for_active_repos()
        expected = [{'repository': 'repo1', 'contributors': {'c1'}}]
        self.assertEqual(response, expected)


@patch("gql.transport.aiohttp.AIOHTTPTransport.__new__", new=MagicMock)
@patch("gql.Client.__new__", new=MagicMock)
@patch("github.Github.__new__", new=MagicMock)
class TestGithubServiceGetReposUserHasContributedTo(unittest.TestCase):
    def test_returns_expected_repos(self):
        github_service = GithubService("", ORGANISATION_NAME)
        repos = github_service.get_repos_user_has_contributed_to(
            login="c1",
            repos_and_contributors=[
                {'repository': 'repo1', 'contributors': {'c1', 'c2'}},
                {'repository': 'repo2', 'contributors': {'c2', 'c3'}},
                {'repository': 'repo3', 'contributors': {'c1', 'c3'}}
            ]
        )
        self.assertEqual(repos, ['repo1', 'repo3'])

    def test_no_repos_contributed_to_returns_empty_list(self):
        github_service = GithubService("", ORGANISATION_NAME)
        repos = github_service.get_repos_user_has_contributed_to(
            login="c5",
            repos_and_contributors=[
                {'repository': 'repo1', 'contributors': {'c1', 'c2'}},
                {'repository': 'repo2', 'contributors': {'c2', 'c3'}},
                {'repository': 'repo3', 'contributors': {'c1', 'c3'}}
            ]
        )
        self.assertEqual(repos, [])

@patch("gql.transport.aiohttp.AIOHTTPTransport.__new__", new=MagicMock)
@patch("gql.Client.__new__", new=MagicMock)
@patch("github.Github.__new__")
class TestGithubServiceUserHasCommitsSince(unittest.TestCase):
    def setUp(self):
        self.repos_and_contributors=[
            {'repository': 'repo1', 'contributors': {'c1', 'c2'}},
            {'repository': 'repo2', 'contributors': {'c2', 'c3'}},
            {'repository': 'repo3', 'contributors': {'c1', 'c3'}}
        ]
        self.since_datetime=datetime(2024, 5, 3)

    def test_user_has_commits_since_true(
            self,
            mock_github_client_core_api
        ):
        github_service = GithubService("", ORGANISATION_NAME)
        github_service.get_repos_user_has_contributed_to = MagicMock(
            return_value=['repo1', 'repo3']
        )
        mock_github_client_core_api.return_value.get_repo.side_effect = [
            MagicMock(get_commits=MagicMock(return_value=MagicMock(totalCount=0))),
            MagicMock(get_commits=MagicMock(return_value=MagicMock(totalCount=20))),
        ]
        response = github_service.user_has_commmits_since(
            login = "c1",
            repos_and_contributors=self.repos_and_contributors,
            since_datetime=self.since_datetime
        )
        self.assertEqual(response, True)

    def test_user_has_commits_since_false_no_commits(
            self,
            mock_github_client_core_api
        ):
        github_service = GithubService("", ORGANISATION_NAME)
        github_service.get_repos_user_has_contributed_to = MagicMock(
            return_value=['repo1', 'repo2']
        )
        mock_github_client_core_api.return_value.get_repo.side_effect = [
            MagicMock(get_commits=MagicMock(return_value=MagicMock(totalCount=0))),
            MagicMock(get_commits=MagicMock(return_value=MagicMock(totalCount=0))),
        ]
        response = github_service.user_has_commmits_since(
            login = "c2",
            repos_and_contributors=self.repos_and_contributors,
            since_datetime=self.since_datetime
        )
        self.assertEqual(response, False)

    def test_user_has_commits_since_false_no_repos(
            self,
            mock_github_client_core_api
        ):
        github_service = GithubService("", ORGANISATION_NAME)
        github_service.get_repos_user_has_contributed_to = MagicMock(
            return_value=[]
        )
        mock_github_client_core_api.return_value.get_repo.side_effect = []
        response = github_service.user_has_commmits_since(
            login = "c5",
            repos_and_contributors=self.repos_and_contributors,
            since_datetime=self.since_datetime
        )
        self.assertEqual(response, False)


@patch("gql.transport.aiohttp.AIOHTTPTransport.__new__", new=MagicMock)
@patch("gql.Client.__new__", new=MagicMock)
@patch("github.Github.__new__", new=MagicMock)
class TestGithubServiceGetPaginatedListOfUnlockedUnarchivedRepos(unittest.TestCase):
    def test_calls_downstream_services(self):
        github_service = GithubService("", ORGANISATION_NAME)
        github_service.get_paginated_list_of_unlocked_unarchived_repos(
            "test_after_cursor"
        )
        github_service.github_client_gql_api.execute.assert_called_once()

    def test_throws_value_error_when_page_size_greater_than_limit(self):
        github_service = GithubService("", ORGANISATION_NAME)
        self.assertRaises(
            ValueError,
            github_service.get_paginated_list_of_unlocked_unarchived_repos,
            "test_after_cursor",
            101
        )


@patch("gql.transport.aiohttp.AIOHTTPTransport.__new__", new=MagicMock)
@patch("gql.Client.__new__", new=MagicMock)
@patch("github.Github.__new__", new=MagicMock)
class TestGithubServiceGetActiveRepositories(unittest.TestCase):
    def setUp(self):
        self.return_data = {
            "organization": {
                "repositories": {
                    "pageInfo": {
                        "endCursor": "repo_1_end_cursor",
                        "hasNextPage": False
                    },
                    "nodes": [
                        {
                            "name": "repository_1",
                            "isDisabled": False,
                        },
                        {
                            "name": "repository_2",
                            "isDisabled": True,
                        },
                        {
                            "name": "repository_3",
                            "isDisabled": False,
                        },
                    ]
                }
            }
        }

    def test_returns_correct_data(self):
        github_service = GithubService("", ORGANISATION_NAME)
        github_service.get_paginated_list_of_unlocked_unarchived_repos = MagicMock(
            return_value=self.return_data
        )
        active_repositories = github_service.get_active_repositories()
        self.assertEqual(len(active_repositories), 2)
        self.assertEqual(set(active_repositories), {"repository_1", "repository_3"})


if __name__ == "__main__":
    unittest.main()
