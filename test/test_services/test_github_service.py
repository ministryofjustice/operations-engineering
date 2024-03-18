import unittest
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock, Mock, call, patch

from freezegun import freeze_time
from github import (Github, GithubException, RateLimitExceededException,
                    UnknownObjectException)
from github.Branch import Branch
from github.Commit import Commit
from github.GitCommit import GitCommit
from github.Issue import Issue
from github.NamedUser import NamedUser
from github.Repository import Repository
from github.Organization import Organization
from github.Team import Team
from github.Variable import Variable
from gql.transport.exceptions import TransportQueryError

from services.github_service import (
    GithubService, retries_github_rate_limit_exception_at_next_reset_once)

ORGANISATION_NAME = "moj-analytical-services"
ENTERPRISE_NAME = "ministry-of-justice-uk"
USER_ACCESS_REMOVED_ISSUE_TITLE = "User access removed, access is now via a team"
TEST_REPOSITORY = "moj-analytical-services/test_repository"

# pylint: disable=E1101, W0212, C2801, R0902


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
class TestGithubServiceArchiveInactiveRepositories(unittest.TestCase):

    # Default for archiving a repository
    def __get_repository(self, last_active_date, archived: bool = False,
                         fork: bool = False,
                         repo_name: str = None, has_commits: bool = True) -> Mock:
        repository_to_consider_for_archiving = Mock(
            Repository, archived=archived, fork=fork)
        repository_to_consider_for_archiving.name = repo_name
        repository_to_consider_for_archiving.get_commits.return_value = [
            Mock(Commit,
                 commit=Mock(GitCommit, author=Mock(NamedUser, date=last_active_date)))] if has_commits else None
        return repository_to_consider_for_archiving

    def setUp(self):
        self.last_active_cutoff_date = datetime.now()
        self.before_cutoff = self.last_active_cutoff_date - timedelta(days=1)
        self.after_cutoff = self.last_active_cutoff_date + timedelta(days=1)

    def test_no_archive_when_repo_is_archived(self, mock_github_client_core_api):
        repo = self.__get_repository(
            last_active_date=self.after_cutoff, archived=True)
        mock_github_client_core_api.return_value.get_organization().get_repos.return_value = [
            repo,
            repo,
            repo
        ]
        GithubService("", ORGANISATION_NAME).archive_all_inactive_repositories(
            self.last_active_cutoff_date, [])
        self.assertEqual(repo.edit.called, False)

    def test_no_archive_when_repo_is_forked(self, mock_github_client_core_api):
        repo = self.__get_repository(
            last_active_date=self.after_cutoff, fork=True)
        mock_github_client_core_api.return_value.get_organization().get_repos.return_value = [
            repo,
            repo,
            repo
        ]
        GithubService("", ORGANISATION_NAME).archive_all_inactive_repositories(
            self.last_active_cutoff_date, [])
        self.assertEqual(repo.edit.called, False)

    def test_no_archive_when_recently_active(self, mock_github_client_core_api):
        repo = self.__get_repository(last_active_date=self.after_cutoff)
        mock_github_client_core_api.return_value.get_organization().get_repos.return_value = [
            repo,
            repo,
            repo
        ]
        GithubService("", ORGANISATION_NAME).archive_all_inactive_repositories(
            self.last_active_cutoff_date, [])
        self.assertEqual(repo.edit.called, False)

    def test_no_archive_when_on_allow_list(self, mock_github_client_core_api):
        repo = self.__get_repository(
            last_active_date=self.after_cutoff, repo_name="allow_me")
        mock_github_client_core_api.return_value.get_organization().get_repos.return_value = [
            repo,
            repo,
            repo
        ]
        GithubService("", ORGANISATION_NAME).archive_all_inactive_repositories(self.last_active_cutoff_date,
                                                                               ["allow_me"])
        self.assertEqual(repo.edit.called, False)

    def test_no_archive_when_repo_has_no_commits_even_if_before_cutoff(self, mock_github_client_core_api):
        repo = self.__get_repository(
            last_active_date=self.before_cutoff, has_commits=False)
        mock_github_client_core_api.return_value.get_organization().get_repos.return_value = [
            repo,
            repo,
            repo
        ]
        GithubService("", ORGANISATION_NAME).archive_all_inactive_repositories(
            self.last_active_cutoff_date, [])
        self.assertEqual(repo.edit.called, False)

    def test_archives_inactive_repositories_not_on_allow_list(self, mock_github_client_core_api):
        repo = self.__get_repository(self.before_cutoff)
        repo_on_allow_list = self.__get_repository(
            self.before_cutoff, repo_name="allow_this")
        mock_github_client_core_api.return_value.get_organization().get_repos.return_value = [
            Mock(Repository, archived=False, fork=True),
            repo,
            Mock(Repository, archived=True, fork=True),
            Mock(Repository, archived=False, fork=True),
            repo,
            Mock(Repository, archived=True, fork=True),
            Mock(Repository, archived=True, fork=False),
            repo_on_allow_list,
            repo_on_allow_list,
        ]

        GithubService("", ORGANISATION_NAME).archive_all_inactive_repositories(self.last_active_cutoff_date,
                                                                               ["allow_this"])

        repo.edit.assert_has_calls(
            [call(archived=True), call(archived=True)])


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
            [call(), call(f"{ORGANISATION_NAME}/test"), call().get_issues()])
        github_service.github_client_core_api.get_repo("mock_full_name_or_id").get_issues.assert_has_calls(
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
    def test_calls_downstream_services(self, _mock_github_client_core_api):
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
    def test_calls_downstream_services(self, _mock_github_client_core_api):
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
            call(ORGANISATION_NAME),
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
            call(ORGANISATION_NAME),
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
            call(ORGANISATION_NAME),
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
            call(), call(ORGANISATION_NAME), call().get_teams()
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
            call(ORGANISATION_NAME),
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
            call(ORGANISATION_NAME),
            call().get_team(1),
            call().get_team().update_team_repository('mock_test_repository', 'pull')
        ])

    def test_updates_permission_to_push_when_permission_write(self, mock_github_client_core_api):
        mock_github_client_core_api.return_value.get_repo.return_value = "mock_test_repository"
        github_service = GithubService("", ORGANISATION_NAME)
        github_service.amend_team_permissions_for_repository(
            1, "write", "test_repository")
        github_service.github_client_core_api.get_organization.assert_has_calls([
            call(ORGANISATION_NAME),
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

    @patch("services.github_service.GithubService.get_support_issues")
    def test_with_correct_issue_but_fail(self, open_issues_mock):
        mock = MagicMock()
        open_issues_mock.return_value = [MagicMock()]

        github_service = GithubService("", ORGANISATION_NAME)

        self.assertRaises(ValueError, github_service.assign_support_issues_to_self,
                          "test_repository_name", "test_org", mock.name)

    @patch("services.github_service.GithubService.get_support_issues")
    def test_with_correct_issue(self, open_issues_mock):
        mock_issue = MockGithubIssue(
            123, 456, "test complete", [], ["test_support_label"])
        open_issues_mock.return_value = [mock_issue]

        github_service = GithubService("", ORGANISATION_NAME)

        issues = github_service.assign_support_issues_to_self(
            "test_repository_name", "test_org", "test_support_label")

        self.assertEqual(issues, [mock_issue])

    @patch("services.github_service.GithubService.get_open_issues_from_repo")
    def test_get_support_issues(self, mock_get_open_issues_from_repo):
        mock_issue = MockGithubIssue(
            123, 456, "test getting issue", [], ["test_support_label"])
        mock_get_open_issues_from_repo.return_value = [mock_issue]
        github_service = GithubService("", ORGANISATION_NAME)

        issues = github_service.get_support_issues(
            "test_org/get_support", mock_issue.labels[0].name)

        self.assertEqual(issues, [mock_issue])

    @patch("services.github_service.GithubService.get_open_issues_from_repo")
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
            call(ORGANISATION_NAME),
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

    def test_calls_downstream_services(self, _mock_github_client_core_api):
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

    def test_calls_downstream_services(self, _mock_github_client_core_api):
        github_service = GithubService("", ORGANISATION_NAME)
        github_service.get_a_team_usernames("some-team")
        github_service.github_client_core_api.get_organization.assert_has_calls([
            call(ORGANISATION_NAME),
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
class TestGithubServiceGetOrgRepoNames(unittest.TestCase):
    def setUp(self):
        self.return_data = {
            "organization": {
                "repositories": {
                    "edges": [
                        {
                            "node": {
                                "name": "test_repository",
                                "isArchived": False,
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
        self.return_data["organization"]["repositories"]["edges"][0]["node"]["isArchived"] = True
        github_service.get_paginated_list_of_org_repository_names = MagicMock(
            return_value=self.return_data
        )
        repos = github_service.get_org_repo_names()
        self.assertEqual(len(repos), 0)
        self.return_data["organization"]["repositories"]["edges"][0]["node"]["isArchived"] = False

        self.return_data["organization"]["repositories"]["edges"][0]["node"]["isLocked"] = True
        github_service.get_paginated_list_of_org_repository_names = MagicMock(
            return_value=self.return_data
        )
        repos = github_service.get_org_repo_names()
        self.assertEqual(len(repos), 0)
        self.return_data["organization"]["repositories"]["edges"][0]["node"]["isLocked"] = False

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
@patch("github.Github.__new__")
class TestGithubServiceCloseRepositoryOpenIssuesWithTag(unittest.TestCase):
    def test_calls_downstream_services_when_no_issues_to_close(self, _mock_github_client_core_api):
        github_service = GithubService("", ORGANISATION_NAME)
        github_service.close_repository_open_issues_with_tag(
            "test_repository", "test-tag")
        github_service.github_client_core_api.get_repo.assert_has_calls([
            call(TEST_REPOSITORY),
            call().get_issues(state='open'),
            call().get_issues().__iter__()
        ])

    def test_closes_open_issues_with_tag(self, mock_github_client_core_api):
        mock_open_issue_with_tag = Mock(Issue, state="open", labels=[
            SimpleNamespace(name="test-tag")])
        mock_github_client_core_api.return_value.get_repo.return_value.get_issues.return_value = [
            mock_open_issue_with_tag]

        github_service = GithubService("", ORGANISATION_NAME)
        github_service.close_repository_open_issues_with_tag(
            "test_repository", "test-tag")

        github_service.github_client_core_api.get_repo.assert_has_calls([
            call(TEST_REPOSITORY),
            call().get_issues(state='open')
        ])
        mock_open_issue_with_tag.edit.assert_has_calls([call(state='closed')])

    def test_ignores_issues_without_tag(self, mock_github_client_core_api):
        mock_open_issue_without_tag = Mock(Issue, state="open", labels=[
            SimpleNamespace(name="wrong-tag")])
        mock_github_client_core_api.return_value.get_repo.return_value.get_issues.return_value = [
            mock_open_issue_without_tag]

        github_service = GithubService("", ORGANISATION_NAME)
        github_service.close_repository_open_issues_with_tag(
            "test_repository", "test-tag")

        self.assertFalse(mock_open_issue_without_tag.edit.called)


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
        self.assertEqual(response, "-")


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

    def test_remove_list_of_users_from_team(self, mock_github_client_core_api):

        github_service = GithubService("", ORGANISATION_NAME)

        github_service.remove_list_of_users_from_team(
            self.team.name, self.users)
        team_id = github_service.get_team_id_from_team_name(self.team.name)

        mock_github_client_core_api.return_value.get_organization.assert_has_calls(
            [
                call(ORGANISATION_NAME),
                call().get_team(team_id),
                call().get_team().remove_membership(self.user1),
                call().get_team().remove_membership(self.user2),
            ]
        )

    def test_remove_list_of_users_from_team_no_users(self, mock_github_client_core_api):

        github_service = GithubService("", ORGANISATION_NAME)
        team_id = github_service.get_team_id_from_team_name(self.team.name)

        github_service.remove_list_of_users_from_team(self.team.name, [])

        mock_github_client_core_api.return_value.get_organization.assert_has_calls(
            [
                call(ORGANISATION_NAME),
                call().get_team(team_id),
            ]
        )

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

    def test_remove_list_of_users_exception(self, mock_github_client_core_api):
        mock_github_client_core_api.return_value.get_organization().get_team().remove_membership.side_effect = [
            GithubException(status=500, data="test", headers={})
        ]
        github_service = GithubService("", ORGANISATION_NAME)

        with self.assertLogs(level='ERROR') as cm:
            github_service.remove_list_of_users_from_team(
                self.team.name, self.users)
            self.assertEqual(
                f"ERROR:root:An exception occurred while removing user user1 from team {self.team.name}", cm.output[0])


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

    def test_get_all_organisations_in_enterprise(self, mock_github_client_rest_api, mock_github_client_core_api):
        mock_github_client_core_api.return_value.get_user().get_orgs.return_value = [
            Mock(Organization, login="org1"),
            Mock(Organization, login="org2"),
        ]

        response = GithubService("", ORGANISATION_NAME).get_all_organisations_in_enterprise()

        self.assertEqual(["org1", "org2"], response)

    def test_get_gha_minutes_used_for_organisation(self, mock_github_client_rest_api, mock_github_client_core_api):
        github_service = GithubService("", ORGANISATION_NAME)
        github_service.github_client_rest_api = mock_github_client_rest_api
        github_service.get_gha_minutes_used_for_organisation("org1")
        mock_github_client_rest_api.assert_has_calls(
            [
                call.get('https://api.github.com/orgs/org1/settings/billing/actions', headers={'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'})
            ]
        )

    def test_modify_gha_minutes_quota_threshold(self, mock_github_client_rest_api, mock_github_client_core_api):
        github_service = GithubService("", ORGANISATION_NAME)
        github_service.github_client_rest_api = mock_github_client_rest_api
        github_service.modify_gha_minutes_quota_threshold(80)
        mock_github_client_rest_api.assert_has_calls(
            [
                call.patch('https://api.github.com/repos/ministryofjustice/operations-engineering/actions/variables/GHA_MINUTES_QUOTA_THRESHOLD', '{"value": "80"}', headers={'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'})
            ]
        )

    def test_get_gha_minutes_quota_threshold(self, mock_github_client_rest_api, mock_github_client_core_api):
        mock_github_client_core_api.return_value.get_repo().get_variable.return_value = Mock(Variable, name="GHA_MINUTES_QUOTA_THRESHOLD", value="70" )

        response = GithubService("", ORGANISATION_NAME).get_gha_minutes_quota_threshold()

        self.assertEqual(70, response)

    @freeze_time("2021-02-01")
    @patch.object(GithubService, "modify_gha_minutes_quota_threshold")
    def test_reset_alerting_threshold_if_first_day_of_month(self, mock_modify_gha_minutes_quota_threshold, mock_github_client_rest_api, mock_github_client_core_api):
        github_service = GithubService("", ORGANISATION_NAME)

        github_service.reset_alerting_threshold_if_first_day_of_month()

        mock_modify_gha_minutes_quota_threshold.assert_called_once_with(70)

    @freeze_time("2021-02-22")
    @patch.object(GithubService, "modify_gha_minutes_quota_threshold")
    def test_reset_alerting_threshold_if_not_first_day_of_month(self, mock_modify_gha_minutes_quota_threshold, mock_github_client_rest_api, mock_github_client_core_api):
        github_service = GithubService("", ORGANISATION_NAME)

        github_service.reset_alerting_threshold_if_first_day_of_month()

        assert not mock_modify_gha_minutes_quota_threshold.called

    @patch.object(GithubService, "get_gha_minutes_used_for_organisation")
    def test_calculate_total_minutes_used(self, mock_get_gha_minutes_used_for_organisation, mock_github_client_rest_api, mock_github_client_core_api):
        github_service = GithubService("", ORGANISATION_NAME)

        mock_get_gha_minutes_used_for_organisation.return_value = { "total_minutes_used": 10 }

        self.assertEqual(github_service.calculate_total_minutes_used(["org1", "org2"]), 20)

    @patch.object(GithubService, "get_gha_minutes_quota_threshold")
    @patch.object(GithubService, "reset_alerting_threshold_if_first_day_of_month")
    @patch.object(GithubService, "calculate_total_minutes_used")
    @patch.object(GithubService, "get_all_organisations_in_enterprise")
    def test_alert_on_low_quota_if_low(self, 
        mock_get_all_organisations_in_enterprise, 
        mock_calculate_total_minutes_used,
        mock_reset_alerting_threshold_if_first_day_of_month,
        mock_get_gha_minutes_quota_threshold,
        mock_github_client_rest_api, 
        mock_github_client_core_api
    ):
        github_service = GithubService("", ORGANISATION_NAME)

        mock_get_all_organisations_in_enterprise.return_value = ["org1", "org2"]
        mock_calculate_total_minutes_used.return_value = 37500
        mock_get_gha_minutes_quota_threshold.return_value = 70

        result = github_service.check_if_quota_is_low()

        mock_reset_alerting_threshold_if_first_day_of_month.assert_called_once()
        self.assertEqual(result['threshold'], 70)
        self.assertEqual(result['percentage_used'], 75)

    @patch.object(GithubService, "get_gha_minutes_quota_threshold")
    @patch.object(GithubService, "reset_alerting_threshold_if_first_day_of_month")
    @patch.object(GithubService, "calculate_total_minutes_used")
    @patch.object(GithubService, "get_all_organisations_in_enterprise")
    def test_alert_on_low_quota_if_not_low(self, 
        mock_get_all_organisations_in_enterprise, 
        mock_calculate_total_minutes_used,
        mock_reset_alerting_threshold_if_first_day_of_month,
        mock_get_gha_minutes_quota_threshold,
        mock_github_client_rest_api, 
        mock_github_client_core_api
    ):
        github_service = GithubService("", ORGANISATION_NAME)

        mock_get_all_organisations_in_enterprise.return_value = ["org1", "org2"]
        mock_calculate_total_minutes_used.return_value = 5000
        mock_get_gha_minutes_quota_threshold.return_value = 70

        result = github_service.check_if_quota_is_low()

        mock_reset_alerting_threshold_if_first_day_of_month.assert_called_once()
        self.assertEqual(result, False)

if __name__ == "__main__":
    unittest.main()
