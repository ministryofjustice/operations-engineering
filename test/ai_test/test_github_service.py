import unittest
from unittest.mock import MagicMock, Mock, patch, call
from freezegun import freeze_time
from datetime import datetime, timedelta
from github import (Github, GithubException, NamedUser, RateLimitExceededException,
                    UnknownObjectException)
from github.Branch import Branch
from github.Commit import Commit
from github.GitCommit import GitCommit
from github.Organization import Organization
from github.Repository import Repository
from github.Variable import Variable
from gql.transport.exceptions import TransportQueryError
from requests import Session

from services.github_service import (
    GithubService, retries_github_rate_limit_exception_at_next_reset_once)

# pylint: disable=E1101

ORGANISATION_NAME = "moj-analytical-services"
ENTERPRISE_NAME = "ministry-of-justice-uk"
USER_ACCESS_REMOVED_ISSUE_TITLE = "User access removed, access is now via a team"
TEST_REPOSITORY = "moj-analytical-services/test_repository"


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
        mock_team = Mock()
        mock_team.get_members.return_value = [user_1, user_2]
        mock_github_client_core_api.return_value.get_organization().get_team.return_value = mock_team
        mock_response = Mock()
        mock_response.__getitem__.return_value = {
            "data": {
                "organization": {
                    "membersWithRole": {
                        "edges": [
                            {"node": {"login": "user_1"}},
                            {"node": {"login": "user_2"}},
                            {"node": {"login": "user_3"}},
                        ]
                    }
                }
            }
        }
        mock_github_client_gql_api.return_value.execute.return_value = mock_response
        github_service = GithubService("", ORGANISATION_NAME)
        github_service.add_all_users_to_team("team_name")
        mock_team.add_membership.assert_has_calls([call(user_3)])


@patch("gql.transport.aiohttp.AIOHTTPTransport.__new__", new=MagicMock)
@patch("gql.Client.__new__", new=MagicMock)
@patch("github.Github.__new__")
class TestGithubServiceArchiveInactiveRepositories(unittest.TestCase):

    def __get_repository(self, last_active_date: datetime, created_at_date: datetime, archived: bool = False, fork: bool = False, repo_name: str = None, has_commits: bool = True) -> Mock:
        repository_to_consider_for_archiving = Mock(
            Repository, archived=archived, fork=fork)
        repository_to_consider_for_archiving.name = repo_name
        repository_to_consider_for_archiving.created_at = created_at_date
        repository_to_consider_for_archiving.get_commits.return_value = (
            [Mock(Commit, commit=Mock(GitCommit, author=Mock(
                NamedUser, date=last_active_date)))] if has_commits else None
        )
        return repository_to_consider_for_archiving

    def setUp(self):
        self.last_active_cutoff_date = datetime.now()
        self.before_cutoff = self.last_active_cutoff_date - timedelta(days=1)
        self.after_cutoff = self.last_active_cutoff_date + timedelta(days=1)

    def test_no_archive_when_repo_is_archived(self, mock_github_client_core_api):
        repo = self.__get_repository(
            last_active_date=self.after_cutoff, created_at_date=self.after_cutoff, archived=True)
        mock_github_client_core_api.return_value.get_organization().get_repos.return_value = [
            repo,
            repo,
            repo
        ]
        github_service = GithubService("", ORGANISATION_NAME)
        github_service.archive_inactive_repositories(
            self.last_active_cutoff_date, [])
        self.assertEqual(repo.edit.called, False)

    def test_no_archive_when_repo_is_forked(self, mock_github_client_core_api):
        repo = self.__get_repository(
            last_active_date=self.after_cutoff, created_at_date=self.after_cutoff, fork=True)
        mock_github_client_core_api.return_value.get_organization().get_repos.return_value = [
            repo,
            repo,
            repo
        ]
        github_service = GithubService("", ORGANISATION_NAME)
        github_service.archive_inactive_repositories(
            self.last_active_cutoff_date, [])
        self.assertEqual(repo.edit.called, False)

    def test_no_archive_when_recently_active(self, mock_github_client_core_api):
        repo = self.__get_repository(
            last_active_date=self.after_cutoff, created_at_date=self.after_cutoff)
        mock_github_client_core_api.return_value.get_organization().get_repos.return_value = [
            repo,
            repo,
            repo
        ]
        github_service = GithubService("", ORGANISATION_NAME)
        github_service.archive_inactive_repositories(
            self.last_active_cutoff_date, [])
        self.assertEqual(repo.edit.called, False)

    def test_no_archive_when_recently_created(self, mock_github_client_core_api):
        repo = self.__get_repository(
            last_active_date=self.after_cutoff, created_at_date=self.after_cutoff)
        mock_github_client_core_api.return_value.get_organization().get_repos.return_value = [
            repo,
            repo,
            repo
        ]
        github_service = GithubService("", ORGANISATION_NAME)
        github_service.archive_inactive_repositories(
            self.last_active_cutoff_date, [])
        self.assertEqual(repo.edit.called, False)

    def test_no_archive_when_on_allow_list(self, mock_github_client_core_api):
        repo = self.__get_repository(
            last_active_date=self.before_cutoff, created_at_date=self.before_cutoff, repo_name="allow_me")
        mock_github_client_core_api.return_value.get_organization().get_repos.return_value = [
            repo,
            repo,
            repo
        ]
        github_service = GithubService("", ORGANISATION_NAME)
        github_service.archive_inactive_repositories(self.last_active_cutoff_date,
                                                     ["allow_me"])
        self.assertEqual(repo.edit.called, False)

    def test_no_archive_when_repo_has_no_commits_and_created_after_cutoff(self, mock_github_client_core_api):
        repo = self.__get_repository(
            last_active_date=self.before_cutoff, created_at_date=self.after_cutoff, has_commits=False)
        mock_github_client_core_api.return_value.get_organization().get_repos.return_value = [
            repo,
            repo,
            repo
        ]
        github_service = GithubService("", ORGANISATION_NAME)
        github_service.archive_inactive_repositories(
            self.last_active_cutoff_date, [])
        self.assertEqual(repo.edit.called, False)

    def test_archives_inactive_repositories(self, mock_github_client_core_api):
        repo = self.__get_repository(self.before_cutoff, self.before_cutoff)
        repo_on_allow_list = self.__get_repository(
            self.before_cutoff, self.before_cutoff, repo_name="allow_this")
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

        github_service = GithubService("", ORGANISATION_NAME)
        github_service.archive_inactive_repositories(
            self.last_active_cutoff_date, ["allow_this"])

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
        github_service = GithubService("", ORGANISATION_NAME)
        response = github_service.get_outside_collaborators()
        self.assertEqual(["tom-smith", "john.smith"], response)

    def test_calls_downstream_services(self, mock_github_client_core_api):
        mock_github_client_core_api.return_value.get_organization(
        ).get_outside_collaborators.return_value = []
        github_service = GithubService("", ORGANISATION_NAME)
        github_service.get_outside_collaborators()
        mock_github_client_core_api.return_value.get_organization.assert_has_calls(
            [call(), call(ORGANISATION_NAME), call().get_outside_collaborators()])

    def test_returns_empty_list_when_collaborators_returns_none(self, mock_github_client_core_api):
        mock_github_client_core_api.return_value.get_organization(
        ).get_outside_collaborators.return_value = None
        github_service = GithubService("", ORGANISATION_NAME)
        response = github_service.get_outside_collaborators()
        self.assertEqual([], response)

    def test_returns_exception_when_collaborators_returns_exception(self, mock_github_client_core_api):
        mock_github_client_core_api.return_value.get_organization(
        ).get_outside_collaborators.side_effect = ConnectionError
        github_service = GithubService("", ORGANISATION_NAME)
        self.assertRaises(
            ConnectionError, github_service.get_outside_collaborators)

    def test_returns_exception_when_organization_returns_exception(self, mock_github_client_core_api):
        mock_github_client_core_api.return_value.get_organization.side_effect = ConnectionError
        github_service = GithubService("", ORGANISATION_NAME)
        self.assertRaises(
            ConnectionError, github_service.get_outside_collaborators)
