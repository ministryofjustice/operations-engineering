import unittest
from datetime import datetime, timedelta
from unittest.mock import call, MagicMock, Mock, patch

from freezegun import freeze_time
from github import Github, RateLimitExceededException
from github.NamedUser import NamedUser
from github.Team import Team
from gql.transport.exceptions import TransportQueryError

from .GithubService import GithubService, retries_github_rate_limit_exception_at_next_reset_once

ORGANISATION_NAME = "moj-analytical-services"
USER_ACCESS_REMOVED_ISSUE_TITLE = "User access removed, access is now via a team"


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
        mock_function.assert_has_calls([call(mock_github_service, 'test_arg')], [
                                       call(mock_github_service, 'test_arg')])

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
    def test_function_is_called_twice_when_transport_query_error_raised_once(self):
        mock_function = Mock(
            side_effect=[TransportQueryError(Mock(), Mock(), Mock()), Mock()])
        mock_github_client = Mock(Github)
        mock_github_client.get_rate_limit().graphql.reset = datetime.now()
        mock_github_service = Mock(
            GithubService, github_client_core_api=mock_github_client)
        retries_github_rate_limit_exception_at_next_reset_once(
            mock_function)(mock_github_service, "test_arg")
        mock_function.assert_has_calls([call(mock_github_service, 'test_arg')], [
            call(mock_github_service, 'test_arg')])

    @freeze_time("2023-02-01")
    def test_rate_limit_exception_raised_when_transport_query_error_raised_twice(self):
        mock_function = Mock(side_effect=[
            TransportQueryError(Mock(), Mock(), Mock()),
            TransportQueryError(Mock(), Mock(), Mock())]
        )
        mock_github_client = Mock(Github)
        mock_github_client.get_rate_limit().graphql.reset = datetime.now()
        mock_github_service = Mock(
            GithubService, github_client_core_api=mock_github_client)
        self.assertRaises(TransportQueryError,
                          retries_github_rate_limit_exception_at_next_reset_once(
                              mock_function), mock_github_service,
                          "test_arg")


@patch("gql.transport.aiohttp.AIOHTTPTransport.__new__", new=MagicMock)
@patch("gql.Client.__new__")
@patch("github.Github.__new__")
class TestGithubServiceInit(unittest.TestCase):

    def test_sets_up_class(self, mock_github_client_core_api, mock_github_client_gql_api):
        mock_github_client_core_api.return_value = "test_mock_github_client_core_api"
        mock_github_client_gql_api.return_value = "test_mock_github_client_gql_api"
        github_service = GithubService("", ORGANISATION_NAME)
        self.assertEqual("test_mock_github_client_core_api",
                         github_service.github_client_core_api)
        self.assertEqual("test_mock_github_client_gql_api",
                         github_service.github_client_gql_api)
        self.assertEqual(ORGANISATION_NAME,
                         github_service.organisation_name)


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
@patch("gql.Client.__new__", new=MagicMock)
@patch("github.Github.__new__")
class TestGithubServiceCloseExpiredIssues(unittest.TestCase):
    DATE_BOUNDARY = 45
    ISSUE_STATE_CRITERIA = "open"

    inside_boundary_criteria = None
    on_boundary_criteria = None
    outside_boundary_criteria = None

    def setUp(self):
        now = datetime.now()
        self.inside_boundary_criteria = now - \
            timedelta(days=self.DATE_BOUNDARY + 1)
        self.on_boundary_criteria = now - timedelta(days=self.DATE_BOUNDARY)
        self.outside_boundary_criteria = now - \
            timedelta(days=self.DATE_BOUNDARY - 1)

    def happy_path_base_issue_mock(self, created_at=None, title=None,
                                   state=None) -> MagicMock:
        return MagicMock(created_at=created_at or self.inside_boundary_criteria,
                         title=title or USER_ACCESS_REMOVED_ISSUE_TITLE,
                         state=state or self.ISSUE_STATE_CRITERIA)

    def test_calls_downstream_services(self, mock_github_client_core_api):
        mock_issue = self.happy_path_base_issue_mock()
        mock_github_client_core_api.return_value.get_repo().get_issues.return_value = [
            mock_issue]
        github_service = GithubService("", ORGANISATION_NAME)
        github_service.close_expired_issues("test")
        github_service.github_client_core_api.get_repo.assert_has_calls(
            [call(), call('moj-analytical-services/test'), call().get_issues()])
        github_service.github_client_core_api.get_repo().get_issues.assert_has_calls(
            [call()])

    def test_sets_issues_to_closed_when_criteria_met(self, mock_github_client_core_api):
        mock_issue = self.happy_path_base_issue_mock()
        mock_github_client_core_api.return_value.get_repo().get_issues.return_value = [
            mock_issue]
        GithubService("", ORGANISATION_NAME).close_expired_issues("test")
        self.assertEqual(mock_issue.edit.call_args_list,
                         [call(state='closed')])

    def test_sets_issues_to_closed_when_criteria_met_and_date_is_on_boundary(self, mock_github_client_core_api):
        mock_issue = self.happy_path_base_issue_mock(
            created_at=self.on_boundary_criteria)
        mock_github_client_core_api.return_value.get_repo().get_issues.return_value = [
            mock_issue]
        GithubService("", ORGANISATION_NAME).close_expired_issues("test")
        self.assertEqual(mock_issue.edit.call_args_list,
                         [call(state='closed')])

    def test_does_not_edit_issue_when_title_criteria_not_met(self, mock_github_client_core_api):
        mock_issue = self.happy_path_base_issue_mock(title="INCORRECT_TITLE")
        mock_github_client_core_api.return_value.get_repo().get_issues.return_value = [
            mock_issue]
        GithubService("", ORGANISATION_NAME).close_expired_issues("test")
        self.assertEqual(mock_issue.edit.call_args_list, [])

    def test_does_not_edit_issue_when_state_criteria_not_met(self, mock_github_client_core_api):
        mock_issue = self.happy_path_base_issue_mock(state="INCORRECT_STATE")
        mock_github_client_core_api.return_value.get_repo().get_issues.return_value = [
            mock_issue]
        GithubService("", ORGANISATION_NAME).close_expired_issues("test")
        self.assertEqual(mock_issue.edit.call_args_list, [])

    def test_does_not_edit_issue_when_empty_list(self, mock_github_client_core_api):
        mock_issue = self.happy_path_base_issue_mock()
        mock_github_client_core_api.return_value.get_repo().get_issues.return_value = []
        GithubService("", ORGANISATION_NAME).close_expired_issues("test")
        self.assertEqual(mock_issue.edit.call_args_list, [])

    def test_does_not_edit_issue_when_none_provided(self, mock_github_client_core_api):
        mock_issue = self.happy_path_base_issue_mock()
        mock_github_client_core_api.return_value.get_repo().get_issues.return_value = None
        GithubService("", ORGANISATION_NAME).close_expired_issues("test")
        self.assertEqual(mock_issue.edit.call_args_list, [])

    def test_throws_exception_when_client_throws_exception(self, mock_github_client_core_api):
        mock_github_client_core_api.return_value.get_repo = MagicMock(
            side_effect=ConnectionError)
        github_service = GithubService("", ORGANISATION_NAME)
        self.assertRaises(
            ConnectionError, github_service.close_expired_issues, "test")


@patch("gql.transport.aiohttp.AIOHTTPTransport.__new__", new=MagicMock)
@patch("gql.Client.__new__", new=MagicMock)
@patch("github.Github.__new__")
class TestGithubServiceCreateAnAccessRemovedIssueForUserInRepository(unittest.TestCase):
    def test_calls_downstream_services(self, mock_github_client_core_api):
        github_service = GithubService("", ORGANISATION_NAME)
        github_service.create_an_access_removed_issue_for_user_in_repository(
            "test_user", "test_repository")
        github_service.github_client_core_api.get_repo.assert_has_calls(
            [call('moj-analytical-services/test_repository'),
             call().create_issue(title=USER_ACCESS_REMOVED_ISSUE_TITLE, assignee='test_user',
                                 body='Hi there\n\nThe user test_user had Direct Member access to this repository and access via a team.\n\nAccess is now only via a team.\n\nYou may have less access it is dependant upon the teams access to the repo.\n\nIf you have any questions, please post in [#ask-operations-engineering](https://mojdt.slack.com/archives/C01BUKJSZD4) on Slack.\n\nThis issue can be closed.')]

        )

    def test_throws_exception_when_client_throws_exception(self, mock_github_client_core_api):
        mock_github_client_core_api.return_value.get_repo = MagicMock(
            side_effect=ConnectionError)
        github_service = GithubService("", ORGANISATION_NAME)
        self.assertRaises(
            ConnectionError, github_service.create_an_access_removed_issue_for_user_in_repository, "test_user",
            "test_repository")


@patch("gql.transport.aiohttp.AIOHTTPTransport.__new__", new=MagicMock)
@patch("gql.Client.__new__", new=MagicMock)
@patch("github.Github.__new__")
class TestGithubServiceRemoveUserFromRepository(unittest.TestCase):
    def test_calls_downstream_services(self, mock_github_client_core_api):
        github_service = GithubService("", ORGANISATION_NAME)
        github_service.remove_user_from_repository(
            "test_user", "test_repository")
        github_service.github_client_core_api.get_repo.assert_has_calls([
            call('moj-analytical-services/test_repository'),
            call().remove_from_collaborators('test_user')
        ])

    def test_throws_exception_when_client_throws_exception(self, mock_github_client_core_api):
        mock_github_client_core_api.return_value.get_repo = MagicMock(
            side_effect=ConnectionError)
        github_service = GithubService("", ORGANISATION_NAME)
        self.assertRaises(
            ConnectionError, github_service.remove_user_from_repository, "test_user",
            "test_repository")


@patch("gql.transport.aiohttp.AIOHTTPTransport.__new__", new=MagicMock)
@patch("gql.Client.__new__", new=MagicMock)
@patch("github.Github.__new__")
class TestGithubServiceGetUserPermissionForRepository(unittest.TestCase):
    def test_calls_downstream_services(self, mock_github_client_core_api):
        mock_github_client_core_api.return_value.get_user.return_value = "mock_user"
        github_service = GithubService("", ORGANISATION_NAME)
        github_service.get_user_permission_for_repository(
            "test_user", "test_repository")
        github_service.github_client_core_api.get_user.assert_has_calls([
                                                                        call('test_user')])
        github_service.github_client_core_api.get_repo.assert_has_calls([
            call('moj-analytical-services/test_repository'),
            call().get_collaborator_permission('mock_user')
        ])

    def test_throws_exception_when_client_throws_exception(self, mock_github_client_core_api):
        mock_github_client_core_api.return_value.get_repo = MagicMock(
            side_effect=ConnectionError)
        github_service = GithubService("", ORGANISATION_NAME)
        self.assertRaises(
            ConnectionError, github_service.get_user_permission_for_repository, "test_user",
            "test_repository")


@patch("gql.transport.aiohttp.AIOHTTPTransport.__new__", new=MagicMock)
@patch("gql.Client.__new__", new=MagicMock)
@patch("github.Github.__new__")
class TestGithubServiceRemoveUserFromTeam(unittest.TestCase):
    def test_calls_downstream_services(self, mock_github_client_core_api):
        mock_github_client_core_api.return_value.get_user.return_value = "mock_user"
        github_service = GithubService("", ORGANISATION_NAME)
        github_service.remove_user_from_team("test_user", "test_repository")
        github_service.github_client_core_api.get_user.assert_has_calls([
                                                                        call('test_user')])
        github_service.github_client_core_api.get_organization.assert_has_calls([
            call('moj-analytical-services'),
            call().get_team('test_repository'),
            call().get_team().remove_membership('mock_user')
        ])

    def test_throws_exception_when_client_throws_exception(self, mock_github_client_core_api):
        mock_github_client_core_api.return_value.get_organization = MagicMock(
            side_effect=ConnectionError)
        github_service = GithubService("", ORGANISATION_NAME)
        self.assertRaises(
            ConnectionError, github_service.remove_user_from_team, "test_user", "test_repository")


@patch("gql.transport.aiohttp.AIOHTTPTransport.__new__", new=MagicMock)
@patch("gql.Client.__new__", new=MagicMock)
@patch("github.Github.__new__")
class TestGithubServiceAddUserToTeam(unittest.TestCase):
    def test_calls_downstream_services(self, mock_github_client_core_api):
        mock_github_client_core_api.return_value.get_user.return_value = "mock_user"
        github_service = GithubService("", ORGANISATION_NAME)
        github_service.add_user_to_team("test_user", 1)
        github_service.github_client_core_api.get_user.assert_has_calls([
            call('test_user')])
        github_service.github_client_core_api.get_organization.assert_has_calls([
            call('moj-analytical-services'),
            call().get_team(1),
            call().get_team().add_membership('mock_user')
        ])

    def test_throws_exception_when_client_throws_exception(self, mock_github_client_core_api):
        mock_github_client_core_api.return_value.get_organization = MagicMock(
            side_effect=ConnectionError)
        github_service = GithubService("", ORGANISATION_NAME)
        self.assertRaises(
            ConnectionError, github_service.add_user_to_team, "test_user", 1)


@patch("gql.transport.aiohttp.AIOHTTPTransport.__new__", new=MagicMock)
@patch("gql.Client.__new__", new=MagicMock)
@patch("github.Github.__new__")
class TestGithubServiceCreateNewTeamWithRepository(unittest.TestCase):
    def test_calls_downstream_services(self, mock_github_client_core_api):
        mock_github_client_core_api.return_value.get_repo.return_value = "mock_repo"
        github_service = GithubService("", ORGANISATION_NAME)
        github_service.create_new_team_with_repository(
            "test_team", "test_repository")
        github_service.github_client_core_api.get_repo.assert_has_calls([
            call('moj-analytical-services/test_repository')
        ])
        github_service.github_client_core_api.get_organization.assert_has_calls([
            call('moj-analytical-services'),
            call().create_team('test_team', ['mock_repo'], '', 'closed',
                               'Automated generated team to grant users access to this repository')
        ])

    def test_throws_exception_when_client_throws_exception(self, mock_github_client_core_api):
        mock_github_client_core_api.return_value.get_organization = MagicMock(
            side_effect=ConnectionError)
        github_service = GithubService("", ORGANISATION_NAME)
        self.assertRaises(
            ConnectionError, github_service.create_new_team_with_repository, "test_team", "test_repository")


@patch("gql.transport.aiohttp.AIOHTTPTransport.__new__", new=MagicMock)
@patch("gql.Client.__new__", new=MagicMock)
@patch("github.Github.__new__")
class TestGithubServiceTeamExists(unittest.TestCase):
    mock_unicorn_team = None
    mock_super_team = None

    def setUp(self):
        self.mock_unicorn_team, self.mock_super_team = Mock(Team), Mock(Team)
        # `name` is a reserved value in `Mock()` constructors. So need to mock the values manually.
        self.mock_unicorn_team.name = "unicorn,team"
        self.mock_super_team.name = "super/team"

    def test_calls_downstream_services(self, mock_github_client_core_api):
        mock_github_client_core_api.return_value.get_organization().get_teams.return_value = []
        github_service = GithubService("", ORGANISATION_NAME)
        github_service.team_exists("test_team")
        github_service.github_client_core_api.get_organization.assert_has_calls([
            call(), call('moj-analytical-services'), call().get_teams()
        ])

    def test_returns_true_when_team_name_exists(self, mock_github_client_core_api):
        mock_github_client_core_api.return_value.get_organization().get_teams.return_value = [
            self.mock_unicorn_team,
            self.mock_super_team,
        ]
        self.assertTrue(GithubService(
            "", ORGANISATION_NAME).team_exists("unicorn,team"))

    def test_returns_false_when_team_does_not_exist(self, mock_github_client_core_api):
        mock_github_client_core_api.return_value.get_organization().get_teams.return_value = [
            self.mock_unicorn_team,
            self.mock_super_team,
        ]
        self.assertFalse(GithubService("", ORGANISATION_NAME).team_exists(
            "THIS_TEAM_DOES_NOT_EXIST!"))

    def test_returns_false_when_teams_return_none(self, mock_github_client_core_api):
        mock_github_client_core_api.return_value.get_organization().get_teams.return_value = None
        self.assertFalse(GithubService(
            "", ORGANISATION_NAME).team_exists("test"))

    def test_throws_exception_when_client_throws_exception(self, mock_github_client_core_api):
        mock_github_client_core_api.return_value.get_organization = MagicMock(
            side_effect=ConnectionError)
        github_service = GithubService("", ORGANISATION_NAME)
        self.assertRaises(
            ConnectionError, github_service.team_exists, "test_team")


@patch("gql.transport.aiohttp.AIOHTTPTransport.__new__", new=MagicMock)
@patch("gql.Client.__new__", new=MagicMock)
@patch("github.Github.__new__")
class TestGithubServiceAmendTeamPermissionsForRepository(unittest.TestCase):
    def test_calls_downstream_services(self, mock_github_client_core_api):
        mock_github_client_core_api.return_value.get_repo.return_value = "mock_test_repository"
        github_service = GithubService("", ORGANISATION_NAME)
        github_service.amend_team_permissions_for_repository(
            1, "test_permission", "test_repository")
        github_service.github_client_core_api.get_repo.assert_has_calls([
            call('moj-analytical-services/test_repository')
        ])
        github_service.github_client_core_api.get_organization.assert_has_calls([
            call('moj-analytical-services'),
            call().get_team(1),
            call().get_team().update_team_repository(
                'mock_test_repository', 'test_permission')
        ])

    def test_updates_permission_to_pull_when_permission_read(self, mock_github_client_core_api):
        mock_github_client_core_api.return_value.get_repo.return_value = "mock_test_repository"
        github_service = GithubService("", ORGANISATION_NAME)
        github_service.amend_team_permissions_for_repository(
            1, "read", "test_repository")
        github_service.github_client_core_api.get_organization.assert_has_calls([
            call('moj-analytical-services'),
            call().get_team(1),
            call().get_team().update_team_repository('mock_test_repository', 'pull')
        ])

    def test_updates_permission_to_push_when_permission_write(self, mock_github_client_core_api):
        mock_github_client_core_api.return_value.get_repo.return_value = "mock_test_repository"
        github_service = GithubService("", ORGANISATION_NAME)
        github_service.amend_team_permissions_for_repository(
            1, "write", "test_repository")
        github_service.github_client_core_api.get_organization.assert_has_calls([
            call('moj-analytical-services'),
            call().get_team(1),
            call().get_team().update_team_repository('mock_test_repository', 'push')
        ])

    def test_throws_exception_when_client_throws_exception(self, mock_github_client_core_api):
        mock_github_client_core_api.return_value.get_organization = MagicMock(
            side_effect=ConnectionError)
        github_service = GithubService("", ORGANISATION_NAME)
        self.assertRaises(
            ConnectionError, github_service.amend_team_permissions_for_repository, 1, "test_permission",
            "test_repository")


@patch("gql.transport.aiohttp.AIOHTTPTransport.__new__", new=MagicMock)
@patch("gql.Client.__new__")
@patch("github.Github.__new__", new=MagicMock)
class TestGithubServiceGetTeamIdFromTeamName(unittest.TestCase):
    def test_calls_downstream_services(self, mock_gql_client):
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
class TestGithubServiceGetPaginatedListOfRepositories(unittest.TestCase):
    def test_calls_downstream_services(self):
        github_service = GithubService("", ORGANISATION_NAME)
        github_service.get_paginated_list_of_repositories("test_after_cursor")
        github_service.github_client_gql_api.execute.assert_called_once()

    def test_throws_value_error_when_page_size_greater_than_limit(self):
        github_service = GithubService("", ORGANISATION_NAME)
        self.assertRaises(
            ValueError, github_service.get_paginated_list_of_repositories, "test_after_cursor", 101)


@patch("gql.transport.aiohttp.AIOHTTPTransport.__new__", new=MagicMock)
@patch("gql.Client.__new__", new=MagicMock)
@patch("github.Github.__new__", new=MagicMock)
class TestGithubServiceGetPaginatedListOfUserNamesWithDirectAccessToRepository(unittest.TestCase):
    def test_calls_downstream_services(self):
        github_service = GithubService("", ORGANISATION_NAME)
        github_service.get_paginated_list_of_user_names_with_direct_access_to_repository("test_repository_name",
                                                                                         "test_after_cursor")
        github_service.github_client_gql_api.execute.assert_called_once()

    def test_throws_value_error_when_page_size_greater_than_limit(self):
        github_service = GithubService("", ORGANISATION_NAME)
        self.assertRaises(
            ValueError, github_service.get_paginated_list_of_user_names_with_direct_access_to_repository,
            "test_repository_name", "test_after_cursor", 101)


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


if __name__ == "__main__":
    unittest.main()
