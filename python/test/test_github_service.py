import unittest
from datetime import datetime, timedelta
from unittest.mock import call, MagicMock, Mock, patch

from freezegun import freeze_time
from github import Github, RateLimitExceededException
from github.NamedUser import NamedUser
from github.Team import Team
from gql.transport.exceptions import TransportQueryError

from python.services.github_service import GithubService, retries_github_rate_limit_exception_at_next_reset_once

ORGANISATION_NAME = "moj-analytical-services"
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
    def test_function_is_called_twice_when_transport_query_error_raised_once(self):
        mock_function = Mock(
            side_effect=[TransportQueryError(Mock(), Mock(), Mock()), Mock()])
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
            [call(TEST_REPOSITORY),
             call().create_issue(title=USER_ACCESS_REMOVED_ISSUE_TITLE, assignee='test_user',
                                 body='Hi there\n\nThe user test_user either had direct member access to the repository or had direct member access and access via a team.\n\nAccess is now only via a team.\n\nIf the user was already in a team, then their direct access to the repository has been removed.\n\nIf the user was not in a team, then the user will have been added to an automated generated team named repository-name-<read|write|maintain|admin>-team and their direct access to the repository has been removed.\n\nThe list of Org teams can be found at https://github.com/orgs/ministryofjustice/teams or https://github.com/orgs/moj-analytical-services/teams.\n\nThe user will have the same level of access to the repository via the team.\n\nThe first user added to a team is made a team maintainer, this enables that user to manage the users within the team.\n\nUsers with admin access are added to the admin team as a team maintainer.\n\nIf you have any questions, please contact us in [#ask-operations-engineering](https://mojdt.slack.com/archives/C01BUKJSZD4) on Slack.\n\nThis issue can be closed.')]

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
            call(TEST_REPOSITORY),
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
            call(TEST_REPOSITORY),
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
@patch("gql.Client.__new__")
@patch("github.Github.__new__")
class TestGithubServiceAddUserToTeam(unittest.TestCase):

    def __create_user(self, name: str) -> dict[str, str]:
        return {
            "name": name
        }

    def test_adds_users_not_currently_in_team(self, mock_github_client_core_api, mock_github_client_gql_api):
        mock_github_client_gql_api.return_value.execute.return_value = {
            "organization": {"team": {"databaseId": 1}}}
        mock_github_client_core_api.return_value.get_organization().get_members.return_value = [
            self.__create_user("user_1"), self.__create_user("user_2"),
            self.__create_user("user_3"), self.__create_user("user_4")
        ]
        mock_team = mock_github_client_core_api.return_value.get_organization().get_team()
        mock_team.get_members.return_value = [
            self.__create_user("user_1"), self.__create_user("user_2")
        ]
        mock_github_client_core_api.return_value.get_user.side_effect = [
            "user_3", "user_4"]

        github_service = GithubService("", ORGANISATION_NAME)
        github_service.add_all_users_to_team("test_team_name")
        mock_team.assert_has_calls(
            [call.add_membership('user_3'), call.add_membership('user_4')])

    def test_adds_no_users_when_all_user_already_exist(self, mock_github_client_core_api, mock_github_client_gql_api):
        mock_github_client_gql_api.return_value.execute.return_value = {
            "organization": {"team": {"databaseId": 1}}}
        mock_github_client_core_api.return_value.get_organization().get_members.return_value = [
            self.__create_user("user_1"), self.__create_user("user_2"),
        ]
        mock_team = mock_github_client_core_api.return_value.get_organization().get_team()
        mock_team.get_members.return_value = [
            self.__create_user("user_1"), self.__create_user("user_2")
        ]

        github_service = GithubService("", ORGANISATION_NAME)
        github_service.add_all_users_to_team("test_team_name")
        mock_team.add_membership.assert_not_called()

    def test_throws_exception_when_client_throws_exception(self, mock_github_client_core_api,
                                                           mock_github_client_gql_api):
        mock_github_client_core_api.return_value.get_organization = MagicMock(
            side_effect=ConnectionError)
        github_service = GithubService("", ORGANISATION_NAME)
        self.assertRaises(
            ConnectionError, github_service.add_all_users_to_team, "test_team_name")


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
            call(TEST_REPOSITORY)
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
            call(TEST_REPOSITORY)
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


@patch("gql.transport.aiohttp.AIOHTTPTransport.__new__", new=MagicMock)
@patch("gql.Client.__new__", new=MagicMock)
@patch("github.Github.__new__", new=MagicMock)
class TestGithubServiceAssignSupportToSelf(unittest.TestCase):

    def test_call_with_nothing_to_assign(self):
        github_service = GithubService("", ORGANISATION_NAME)
        issues = github_service.assign_support_issues_to_self(
            "test_repository_name", "test_org", "test_support_label")

        self.assertEqual(issues, [])

    @patch("python.services.github_service.GithubService.get_support_issues")
    def test_with_correct_issue_but_fail(self, open_issues_mock):
        mock = MagicMock()
        open_issues_mock.return_value = [MagicMock()]

        github_service = GithubService("", ORGANISATION_NAME)

        self.assertRaises(ValueError, github_service.assign_support_issues_to_self,
                          "test_repository_name", "test_org", mock.name)

    @patch("python.services.github_service.GithubService.get_support_issues")
    def test_with_correct_issue(self, open_issues_mock):
        mock_issue = MockGithubIssue(
            123, 456, "test complete", [], ["test_support_label"])
        open_issues_mock.return_value = [mock_issue]

        github_service = GithubService("", ORGANISATION_NAME)

        issues = github_service.assign_support_issues_to_self(
            "test_repository_name", "test_org", "test_support_label")

        self.assertEqual(issues, [mock_issue])

    @patch("python.services.github_service.GithubService.get_open_issues_from_repo")
    def test_get_support_issues(self, mock_get_open_issues_from_repo):
        mock_issue = MockGithubIssue(
            123, 456, "test getting issue", [], ["test_support_label"])
        mock_get_open_issues_from_repo.return_value = [mock_issue]
        github_service = GithubService("", ORGANISATION_NAME)

        issues = github_service.get_support_issues(
            "test_org/get_support", mock_issue.labels[0].name)

        self.assertEqual(issues, [mock_issue])

    @patch("python.services.github_service.GithubService.get_open_issues_from_repo")
    def test_get_support_issues_with_no_issues(self, mock_get_open_issues_from_repo):
        mock_get_open_issues_from_repo.return_value = []
        github_service = GithubService("", ORGANISATION_NAME)

        issues = github_service.get_support_issues(
            "test_org/test_with_no_issues", "test_support_label")

        self.assertEqual(issues, [])

    def test_assign_issues_to_self(self):
        mock_issue = MockGithubIssue(
            123, 456, "testing assign", [], ["test_support_label"])
        github_service = GithubService("", ORGANISATION_NAME)

        issues = github_service.assign_issues_to_self(
            [mock_issue], "test_org/test_assign")

        self.assertEqual(issues, [mock_issue])

    def test_assign_issues_to_self_with_no_issues(self):
        github_service = GithubService("", ORGANISATION_NAME)

        issues = github_service.assign_issues_to_self(
            [], "test_org/test_repository_name")

        self.assertEqual(issues, [])


@patch("gql.transport.aiohttp.AIOHTTPTransport.__new__", new=MagicMock)
@patch("gql.Client.__new__", new=MagicMock)
@patch("github.Github.__new__")
class TestGithubServiceMakeUserTeamMaintainer(unittest.TestCase):
    def test_calls_downstream_services(self, mock_github_client_core_api):
        mock_github_client_core_api.return_value.get_user.return_value = "mock_user"
        github_service = GithubService("", ORGANISATION_NAME)
        github_service.add_user_to_team_as_maintainer("test_user", 1)
        github_service.github_client_core_api.get_user.assert_has_calls([
            call('test_user')])
        github_service.github_client_core_api.get_organization.assert_has_calls([
            call('moj-analytical-services'),
            call().get_team(1),
            call().get_team().add_membership('mock_user', 'maintainer')
        ])

    def test_throws_exception_when_client_throws_exception(self, mock_github_client_core_api):
        mock_github_client_core_api.return_value.get_organization = MagicMock(
            side_effect=ConnectionError)
        github_service = GithubService("", ORGANISATION_NAME)
        self.assertRaises(
            ConnectionError, github_service.add_user_to_team_as_maintainer, "test_user", 1)


@patch("gql.transport.aiohttp.AIOHTTPTransport.__new__", new=MagicMock)
@patch("gql.Client.__new__", new=MagicMock)
@patch("github.Github.__new__")
class TestGithubServiceGetRepositoryTeams(unittest.TestCase):

    def test_returns_teams(self, mock_github_client_core_api):
        mock_github_client_core_api.return_value.get_repo().get_teams.return_value = [
            Mock(Team),
            Mock(Team),
        ]
        response = GithubService(
            "", ORGANISATION_NAME).get_repository_teams("some-repo")
        self.assertEqual(2, len(response))

    def test_calls_downstream_services(self, mock_github_client_core_api):
        github_service = GithubService("", ORGANISATION_NAME)
        github_service.get_repository_teams("test_repository")
        github_service.github_client_core_api.get_repo.assert_has_calls(
            [call(TEST_REPOSITORY).get_teams()])

    def test_returns_empty_list_when_teams_returns_none(self, mock_github_client_core_api):
        mock_github_client_core_api.return_value.get_repo().get_teams.return_value = None
        self.assertEqual([], GithubService(
            "", ORGANISATION_NAME).get_repository_teams("test_repository"))

    def test_returns_exception_when_teams_returns_exception(self, mock_github_client_core_api):
        mock_github_client_core_api.return_value.get_repo(
        ).get_teams().side_effect = ConnectionError
        github_service = GithubService("", ORGANISATION_NAME)
        self.assertRaises(
            ConnectionError, github_service.get_repository_teams("test_repository"))


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

    def test_calls_downstream_services(self, mock_github_client_core_api):
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
@patch("gql.Client.__new__", new=MagicMock)
@patch("github.Github.__new__")
class TestGithubServiceGetATeamUsernames(unittest.TestCase):

    def test_returns_team_usernames(self, mock_github_client_core_api):
        mock_github_client_core_api.return_value.get_organization.return_value.get_team_by_slug().get_members.return_value = [
            Mock(NamedUser),
            Mock(NamedUser),
        ]
        response = GithubService(
            "", ORGANISATION_NAME).get_a_team_usernames("some-team")
        self.assertEqual(2, len(response))

    def test_calls_downstream_services(self, mock_github_client_core_api):
        github_service = GithubService("", ORGANISATION_NAME)
        github_service.get_a_team_usernames("some-team")
        github_service.github_client_core_api.get_organization.assert_has_calls([
            call('moj-analytical-services'),
            call().get_team_by_slug('some-team'),
            call().get_team_by_slug().get_members(),
            call().get_team_by_slug().get_members().__bool__(),
            call().get_team_by_slug().get_members().__iter__()
        ])

    def test_returns_empty_list_when_team_usernames_returns_none(self, mock_github_client_core_api):
        mock_github_client_core_api.return_value.get_organization.return_value.get_team_by_slug(
        ).get_members.return_value = None
        self.assertEqual([], GithubService(
            "", ORGANISATION_NAME).get_a_team_usernames("some-team"))

    def test_returns_exception_when_team_usernames_returns_exception(self, mock_github_client_core_api):
        mock_github_client_core_api.return_value.get_organization(
        ).get_team_by_slug().get_members.side_effect = ConnectionError
        github_service = GithubService("", ORGANISATION_NAME)
        self.assertRaises(
            ConnectionError, github_service.get_a_team_usernames, "some-team")


@patch("gql.transport.aiohttp.AIOHTTPTransport.__new__", new=MagicMock)
@patch("gql.Client.__new__")
@patch("github.Github.__new__", new=MagicMock)
class TestGithubServiceGetPaginatedListOfRepositoriesPerType(unittest.TestCase):
    def test_calls_downstream_services(self, mock_gql_client):
        github_service = GithubService("", ORGANISATION_NAME)
        github_service.get_paginated_list_of_repositories_per_type(
            "public", "after_cursor")
        github_service.github_client_gql_api.execute.assert_called_once()

    def test_throws_value_error_when_page_size_greater_than_limit(self, mock_gql_client):
        github_service = GithubService("", ORGANISATION_NAME)
        self.assertRaises(
            ValueError, github_service.get_paginated_list_of_repositories_per_type, "public", "test_after_cursor", 101)


class MockGithubIssue(MagicMock):
    def __init__(self, the_id, number, title, assignees, label):
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


if __name__ == "__main__":
    unittest.main()
