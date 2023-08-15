import json
from calendar import timegm
from datetime import datetime, timedelta
from textwrap import dedent
from time import gmtime, sleep
from typing import Any, Callable

from dateutil.relativedelta import relativedelta
from github import Github, NamedUser, RateLimitExceededException
from github.Commit import Commit
from github.Issue import Issue
from github.Repository import Repository
from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
from gql.transport.exceptions import TransportQueryError
from requests import Session

from python.config.logging_config import logging
from python.services.slack_service import SlackService

logging.getLogger("gql").setLevel(logging.WARNING)


def retries_github_rate_limit_exception_at_next_reset_once(func: Callable) -> Callable:
    def decorator(*args, **kwargs):
        """
        A decorator to retry the method when rate limiting for GitHub resets if the method fails due to Rate Limit related exception.

        WARNING: Since this decorator retries methods, ensure that the method being decorated is idempotent
         or contains only one non-idempotent method at the end of a call chain to GitHub.

         Example of idempotent methods are:
            - Retrieving data
         Example of (potentially) non-idempotent methods are:
            - Deleting data
            - Updating data
        """
        try:
            return func(*args, **kwargs)
        except (RateLimitExceededException, TransportQueryError) as exception:
            logging.warning(
                f"Caught {type(exception).__name__}, retrying calls when rate limit resets.")
            rate_limits = args[0].github_client_core_api.get_rate_limit()
            rate_limit_to_use = rate_limits.core if type(
                exception) is RateLimitExceededException else rate_limits.graphql

            reset_timestamp = timegm(rate_limit_to_use.reset.timetuple())
            now_timestamp = timegm(gmtime())
            time_until_core_api_rate_limit_resets = (
                reset_timestamp - now_timestamp) if reset_timestamp > now_timestamp else 0

            wait_time_buffer = 5
            sleep(time_until_core_api_rate_limit_resets +
                  wait_time_buffer if time_until_core_api_rate_limit_resets else 0)
            return func(*args, **kwargs)

    return decorator


class GithubService:
    USER_ACCESS_REMOVED_ISSUE_TITLE: str = "User access removed, access is now via a team"
    GITHUB_GQL_MAX_PAGE_SIZE = 100
    GITHUB_GQL_DEFAULT_PAGE_SIZE = 80

    # Added to stop TypeError on instantiation. See https://github.com/python/cpython/blob/d2340ef25721b6a72d45d4508c672c4be38c67d3/Objects/typeobject.c#L4444
    def __new__(cls, *_, **__):
        return super(GithubService, cls).__new__(cls)

    def __init__(self, org_token: str, organisation_name: str) -> None:
        self.github_client_core_api: Github = Github(org_token)
        self.github_client_gql_api: Client = Client(transport=AIOHTTPTransport(
            url="https://api.github.com/graphql",
            headers={"Authorization": f"Bearer {org_token}"},
        ), execute_timeout=120)
        self.organisation_name: str = organisation_name
        self.github_client_rest_api = Session()
        self.github_client_rest_api.headers.update(
            {
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {org_token}",
            }
        )

    def archive_all_inactive_repositories(self, last_active_cutoff_date: datetime, allow_list: list[str]) -> None:
        for repo in self.__get_repos_to_consider_for_archiving("all"):
            if self.__is_repo_ready_for_archiving(repo, last_active_cutoff_date, allow_list):
                repo.edit(archived=True)

    def __get_repos_to_consider_for_archiving(self, repository_type: str) -> list[Repository]:
        repositories = list(
            self.github_client_core_api.get_organization(self.organisation_name).get_repos(type=repository_type))
        return [repository for repository in repositories if not (repository.archived or repository.fork)]

    def __is_repo_ready_for_archiving(self, repository, last_active_cutoff_date, allow_list: list[str]) -> bool:
        latest_commit_position = 0
        commit: Commit = None
        try:  # Try block needed as get_commits() can cause exception when a repository has no commits as GH returns negative result.
            commit = repository.get_commits()[latest_commit_position]
        except Exception:
            logging.info(
                f"Manually check repository: {repository.name}. Reason: No commits in repository")
            return False

        if commit.commit.author.date < last_active_cutoff_date:
            if repository.name in allow_list:
                logging.info(
                    f"Skipping repository: {repository.name}. Reason: Present in allow list")
                return False
            return True
        else:
            logging.info(
                f"Skipping repository: {repository.name}. Reason: Last commit date later than last active cutoff date")
            return False

    @retries_github_rate_limit_exception_at_next_reset_once
    def get_outside_collaborators_login_names(self) -> list[str]:
        logging.info("Getting Outside Collaborators Login Names")
        outside_collaborators = self.github_client_core_api.get_organization(
            self.organisation_name).get_outside_collaborators() or []
        return [outside_collaborator.login.lower() for outside_collaborator in outside_collaborators]

    @retries_github_rate_limit_exception_at_next_reset_once
    def close_expired_issues(self, repository_name: str) -> None:
        logging.info(f"Closing expired issues for {repository_name}")
        issues = self.github_client_core_api.get_repo(
            f"{self.organisation_name}/{repository_name}").get_issues() or []
        for issue in issues:
            if self.__is_expired(issue):
                issue.edit(state="closed")
                logging.info(f"Closing issue in {repository_name}")

    def __is_expired(self, issue: Issue) -> bool:
        grace_period = issue.created_at + timedelta(days=45)
        return (issue.title == self.USER_ACCESS_REMOVED_ISSUE_TITLE
                and issue.state == "open"
                and grace_period < datetime.now())

    def assign_support_issues_to_self(self, repository_name, org_name, tag: str) -> list[any]:
        """
            Assigns issues with a specific tag to the user who created the issue.
            This is used to assign support issues to the user who created the issue.

            :param repository_name: The name of the repository to assign issues in.
            :param org_name: The name of the organisation to assign issues in.
            :param tag: The tag to search for.
        """
        name = f"{org_name}/{repository_name}"
        support_issues = self.get_support_issues(name, tag)

        try:
            return self.assign_issues_to_self(support_issues, name)
        except ValueError as error:
            raise ValueError(
                f"Failed to assign issues to self in {repository_name}") from error

    @staticmethod
    def assign_issues_to_self(issues: list[Issue], repository_name: str) -> list[any]:
        for issue in issues:
            issue.edit(assignees=[issue.user.login])
            if len(issue.assignees) == 0:
                raise ValueError(
                    f"Failed to assign issue {issue.number} to {issue.user.login} in {repository_name}")

        return issues

    def get_support_issues(self, repository_name: str, tag: str) -> list[Issue]:
        return [
            issue
            for issue in self.get_open_issues_from_repo(repository_name)
            for label in issue.labels
            if label.name == tag and len(issue.assignees) == 0
        ]

    @retries_github_rate_limit_exception_at_next_reset_once
    def get_open_issues_from_repo(self, repository_name: str) -> list[Issue]:
        """
        Args:
            repository_name: Should be in the format of "organisation/repository"

        Returns:
            A list of open issues in the repository from the GitHub API.
        """
        required_state = "open"
        repo = self.github_client_core_api.get_repo(repository_name)

        return repo.get_issues(state=required_state) or []

    @retries_github_rate_limit_exception_at_next_reset_once
    def create_an_access_removed_issue_for_user_in_repository(self, user_name: str, repository_name: str) -> None:
        logging.info(
            f"Creating an access removed issue for user {user_name} in repository {repository_name}")
        self.github_client_core_api.get_repo(f"{self.organisation_name}/{repository_name}").create_issue(
            title=self.USER_ACCESS_REMOVED_ISSUE_TITLE,
            assignee=user_name,
            body=dedent(f"""
        Hi there

        The user {user_name} either had direct member access to the repository or had direct member access and access via a team.

        Access is now only via a team.

        If the user was already in a team, then their direct access to the repository has been removed.

        If the user was not in a team, then the user will have been added to an automated generated team named repository-name-<read|write|maintain|admin>-team and their direct access to the repository has been removed.

        The list of Org teams can be found at https://github.com/orgs/ministryofjustice/teams or https://github.com/orgs/moj-analytical-services/teams.

        The user will have the same level of access to the repository via the team.

        The first user added to a team is made a team maintainer, this enables that user to manage the users within the team.

        Users with admin access are added to the admin team as a team maintainer.

        If you have any questions, please contact us in [#ask-operations-engineering](https://mojdt.slack.com/archives/C01BUKJSZD4) on Slack.

        This issue can be closed.
        """).strip("\n")
        )

    @retries_github_rate_limit_exception_at_next_reset_once
    def remove_user_from_repository(self, user_name: str, repository_name: str) -> None:
        logging.info(
            f"Removing user {user_name} from repository {repository_name}")
        self.github_client_core_api.get_repo(
            f"{self.organisation_name}/{repository_name}").remove_from_collaborators(user_name)

    @retries_github_rate_limit_exception_at_next_reset_once
    def get_user_permission_for_repository(self, user_name: str, repository_name: str) -> str:
        logging.info(
            f"Getting permissions for user {user_name} from repository {repository_name}")
        user = self.github_client_core_api.get_user(user_name)
        return self.github_client_core_api.get_repo(
            f"{self.organisation_name}/{repository_name}").get_collaborator_permission(user)

    @retries_github_rate_limit_exception_at_next_reset_once
    def remove_user_from_team(self, user_name: str, team_id: int) -> None:
        logging.info(f"Removing user {user_name} from team {team_id}")
        user = self.github_client_core_api.get_user(user_name)
        self.github_client_core_api.get_organization(self.organisation_name).get_team(team_id).remove_membership(
            user)

    @retries_github_rate_limit_exception_at_next_reset_once
    def add_user_to_team(self, user_name: str, team_id: int) -> None:
        logging.info(f"Adding user {user_name} from team {team_id}")
        user = self.github_client_core_api.get_user(user_name)
        self.github_client_core_api.get_organization(
            self.organisation_name).get_team(team_id).add_membership(user)

    def add_all_users_to_team(self, team_name: str) -> None:
        logging.info(f"Adding all users to {team_name}")
        team_id = self.get_team_id_from_team_name(team_name)
        all_users = self.__get_all_users()
        existing_users_in_team = self.__get_users_from_team(team_id)

        for user in all_users:
            if user not in existing_users_in_team:
                self.__add_user_to_team(user, team_id)

    @retries_github_rate_limit_exception_at_next_reset_once
    def __get_all_users(self) -> list:
        logging.info("Getting all organization members")
        return self.github_client_core_api.get_organization(self.organisation_name).get_members() or []

    @retries_github_rate_limit_exception_at_next_reset_once
    def __add_user_to_team(self, user: NamedUser, team_id: int) -> None:
        logging.info(f"Adding user {user.name} to team {team_id}")
        self.github_client_core_api.get_organization(
            self.organisation_name).get_team(team_id).add_membership(user)

    @retries_github_rate_limit_exception_at_next_reset_once
    def __get_users_from_team(self, team_id: int) -> list:
        logging.info(f"Getting all named users for team {team_id}")
        return self.github_client_core_api.get_organization(self.organisation_name).get_team(
            team_id).get_members() or []

    @retries_github_rate_limit_exception_at_next_reset_once
    def create_new_team_with_repository(self, team_name: str, repository_name: str) -> None:
        logging.info(
            f"Creating team {team_name} for repository {repository_name}")
        repo = self.github_client_core_api.get_repo(
            f"{self.organisation_name}/{repository_name}")
        self.github_client_core_api.get_organization(self.organisation_name).create_team(
            team_name,
            [repo],
            "",
            "closed",
            "Automated generated team to grant users access to this repository",
        )

    @retries_github_rate_limit_exception_at_next_reset_once
    def team_exists(self, team_name) -> bool:
        logging.info(f"Checking if team {team_name} exists")
        github_teams = self.github_client_core_api.get_organization(
            self.organisation_name).get_teams() or []
        return any(github_team.name == team_name for github_team in github_teams)

    @retries_github_rate_limit_exception_at_next_reset_once
    def amend_team_permissions_for_repository(self, team_id: int, permission: str, repository_name: str) -> None:
        logging.info(
            f"Amending permissions for team {team_id} in repository {repository_name}")
        if permission == "read":
            permission = "pull"
        elif permission == "write":
            permission = "push"
        repo = self.github_client_core_api.get_repo(
            f"{self.organisation_name}/{repository_name}")
        self.github_client_core_api.get_organization(self.organisation_name).get_team(
            team_id).update_team_repository(repo, permission)

    @retries_github_rate_limit_exception_at_next_reset_once
    def get_team_id_from_team_name(self, team_name: str) -> int | TypeError:
        logging.info(f"Getting team ID for team name {team_name}")
        data = self.github_client_gql_api.execute(gql("""
            query($organisation_name: String!, $team_name: String!) {
                organization(login: $organisation_name) {
                    team(slug: $team_name) {
                        databaseId
                    }
                }
            }
        """), variable_values={"organisation_name": self.organisation_name, "team_name": team_name})

        return data["organization"]["team"]["databaseId"]

    @retries_github_rate_limit_exception_at_next_reset_once
    def get_paginated_list_of_repositories(self, after_cursor: str | None,
                                           page_size: int = GITHUB_GQL_DEFAULT_PAGE_SIZE) -> dict[str, Any]:
        logging.info(
            f"Getting paginated list of repositories. Page size {page_size}, after cursor {bool(after_cursor)}")
        if page_size > self.GITHUB_GQL_MAX_PAGE_SIZE:
            raise ValueError(
                f"Page size of {page_size} is too large. Max page size {self.GITHUB_GQL_MAX_PAGE_SIZE}")
        return self.github_client_gql_api.execute(gql("""
            query($organisation_name: String!, $page_size: Int!, $after_cursor: String) {
                organization(login: $organisation_name) {
                    repositories(first: $page_size, after: $after_cursor) {
                        pageInfo {
                            endCursor
                            hasNextPage
                        }
                        edges {
                            node {
                                isArchived
                                isDisabled
                                isPrivate
                                isLocked
                                name
                                pushedAt
                                url
                                description
                                hasIssuesEnabled
                                defaultBranchRef {
                                    name
                                }
                                licenseInfo {
                                    name
                                }
                                branchProtectionRules(first: 10) {
                                    edges {
                                        node {
                                            isAdminEnforced
                                            pattern
                                            requiredApprovingReviewCount
                                            requiresApprovingReviews
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        """), variable_values={"organisation_name": self.organisation_name, "page_size": page_size,
                               "after_cursor": after_cursor})

    @retries_github_rate_limit_exception_at_next_reset_once
    def get_paginated_list_of_user_names_with_direct_access_to_repository(self, repository_name: str,
                                                                          after_cursor: str | None,
                                                                          page_size: int = GITHUB_GQL_DEFAULT_PAGE_SIZE) -> \
            dict[str, Any]:
        logging.info(
            f"Getting paginated list of user names with direct access to repository {repository_name}. Page size {page_size}, after cursor {bool(after_cursor)}"
        )
        if page_size > self.GITHUB_GQL_MAX_PAGE_SIZE:
            raise ValueError(
                f"Page size of {page_size} is too large. Max page size {self.GITHUB_GQL_MAX_PAGE_SIZE}")
        return self.github_client_gql_api.execute(gql("""
            query($organisation_name: String!, $repository_name: String!, $page_size: Int!, $after_cursor: String) {
                repository(name: $repository_name, owner: $organisation_name) {
                    collaborators(first: $page_size, after:$after_cursor, affiliation: DIRECT) {
                        edges {
                            node {
                                login
                            }
                        }
                        pageInfo {
                            hasNextPage
                            endCursor
                        }
                    }
                }
            }
        """), variable_values={
            "repository_name": repository_name,
            "organisation_name": self.organisation_name,
            "page_size": page_size,
            "after_cursor": after_cursor
        })

    @retries_github_rate_limit_exception_at_next_reset_once
    def get_paginated_list_of_team_names(self, after_cursor: str | None,
                                         page_size: int = GITHUB_GQL_DEFAULT_PAGE_SIZE) -> dict[str, Any]:
        logging.info(
            f"Getting paginated list of team names. Page size {page_size}, after cursor {bool(after_cursor)}")
        if page_size > self.GITHUB_GQL_MAX_PAGE_SIZE:
            raise ValueError(
                f"Page size of {page_size} is too large. Max page size {self.GITHUB_GQL_MAX_PAGE_SIZE}")
        return self.github_client_gql_api.execute(gql("""
            query($organisation_name: String!, $page_size: Int!, $after_cursor: String) {
                organization(login: $organisation_name) {
                    teams(first: $page_size, after:$after_cursor) {
                        pageInfo {
                            endCursor
                            hasNextPage
                        }
                        edges {
                            node {
                                slug
                            }
                        }
                    }
                }
            }
        """), variable_values={
            "organisation_name": self.organisation_name,
            "page_size": page_size,
            "after_cursor": after_cursor
        })

    @retries_github_rate_limit_exception_at_next_reset_once
    def get_paginated_list_of_team_repositories(self, team_name: str, after_cursor: str | None,
                                                page_size: int = GITHUB_GQL_DEFAULT_PAGE_SIZE) -> dict[str, Any]:
        logging.info(
            f"Getting paginated list of team repos. Page size {page_size}, after cursor {bool(after_cursor)}")
        if page_size > self.GITHUB_GQL_MAX_PAGE_SIZE:
            raise ValueError(
                f"Page size of {page_size} is too large. Max page size {self.GITHUB_GQL_MAX_PAGE_SIZE}")
        return self.github_client_gql_api.execute(gql("""
        query($organisation_name: String!, $team_name: String!, $page_size: Int!, $after_cursor: String) {
            organization(login: $organisation_name) {
                team(slug: $team_name) {
                    repositories(first: $page_size, after:$after_cursor) {
                        edges {
                            node {
                                name
                            }
                        }
                        pageInfo {
                            endCursor
                            hasNextPage
                        }
                    }
                }
            }
        }
        """), variable_values={
            "organisation_name": self.organisation_name,
            "team_name": team_name,
            "page_size": page_size,
            "after_cursor": after_cursor
        })

    def fetch_all_repositories_in_org(self) -> list[dict[str, Any]]:
        """A wrapper function to run a GraphQL query to get the list of repositories in the organisation

        Returns:
            list: A list of the organisation repos names
        """
        has_next_page = True
        after_cursor = None
        repos = []

        #  Disable logging. The output is too verbose and not required.
        logging.getLogger("gql").setLevel(logging.CRITICAL)
        logging.disable(logging.INFO)

        while has_next_page:
            data = self.get_paginated_list_of_repositories(after_cursor, 50)

            if data["organization"]["repositories"]["edges"] is not None:
                for repo in data["organization"]["repositories"]["edges"]:
                    if not (
                        repo["node"]["isDisabled"]
                        or repo["node"]["isArchived"]
                        or repo["node"]["isLocked"]
                    ):
                        repos.append(repo)

            has_next_page = data["organization"]["repositories"]["pageInfo"]["hasNextPage"]
            after_cursor = data["organization"]["repositories"]["pageInfo"]["endCursor"]
        return repos

    @retries_github_rate_limit_exception_at_next_reset_once
    def get_paginated_list_of_team_user_names(self, team_name: str, after_cursor: str | None,
                                              page_size: int = GITHUB_GQL_DEFAULT_PAGE_SIZE) -> dict[str, Any]:

        logging.info(
            f"Getting paginated list of team repos. Page size {page_size}, after cursor {bool(after_cursor)}")
        if page_size > self.GITHUB_GQL_MAX_PAGE_SIZE:
            raise ValueError(
                f"Page size of {page_size} is too large. Max page size {self.GITHUB_GQL_MAX_PAGE_SIZE}")
        return self.github_client_gql_api.execute(gql("""
        query($organisation_name: String!, $team_name: String!, $page_size: Int!, $after_cursor: String) {
            organization(login: $organisation_name) {
                team(slug: $team_name) {
                    members(first: $page_size, after: $after_cursor) {
                        edges {
                            node {
                                login
                            }
                        }
                        pageInfo {
                            hasNextPage
                            endCursor
                        }
                    }
                }
            }
        }
        """), variable_values={
            "organisation_name": self.organisation_name,
            "team_name": team_name,
            "page_size": page_size,
            "after_cursor": after_cursor
        })

    @retries_github_rate_limit_exception_at_next_reset_once
    def add_user_to_team_as_maintainer(self, user_name: str, team_id: int) -> None:
        logging.info(f"Making user {user_name} a maintainer in team {team_id}")
        user = self.github_client_core_api.get_user(user_name)
        self.github_client_core_api.get_organization(
            self.organisation_name).get_team(team_id).add_membership(user, "maintainer")

    @retries_github_rate_limit_exception_at_next_reset_once
    def get_repository_teams(self, repository_name: str) -> list:
        teams = self.github_client_core_api.get_repo(
            f"{self.organisation_name}/{repository_name}").get_teams() or []
        return teams

    @retries_github_rate_limit_exception_at_next_reset_once
    def get_repository_direct_users(self, repository_name: str) -> list:
        users = self.github_client_core_api.get_repo(
            f"{self.organisation_name}/{repository_name}").get_collaborators("direct") or []
        return [member.login.lower() for member in users]

    @retries_github_rate_limit_exception_at_next_reset_once
    def get_a_team_usernames(self, team_name: str) -> list[str]:
        members = self.github_client_core_api.get_organization(
            self.organisation_name).get_team_by_slug(team_name).get_members() or []
        return [member.login.lower() for member in members]

    @retries_github_rate_limit_exception_at_next_reset_once
    def get_paginated_list_of_repositories_per_type(self, repo_type: str, after_cursor: str | None,
                                                    page_size: int = GITHUB_GQL_DEFAULT_PAGE_SIZE) -> dict[str, Any]:
        logging.info(
            f"Getting paginated list of repositories per type {repo_type}. Page size {page_size}, after cursor {bool(after_cursor)}")
        if page_size > self.GITHUB_GQL_MAX_PAGE_SIZE:
            raise ValueError(
                f"Page size of {page_size} is too large. Max page size {self.GITHUB_GQL_MAX_PAGE_SIZE}")
        the_query = f"org:{self.organisation_name}, archived:false, is:{repo_type}"
        query = gql("""
            query($page_size: Int!, $after_cursor: String, $the_query: String!) {
                search(
                    type: REPOSITORY
                    query: $the_query
                    first: $page_size
                    after: $after_cursor
                ) {
                repos: edges {
                    repo: node {
                        ... on Repository {
                                name
                                isDisabled
                                isLocked
                                hasIssuesEnabled
                                collaborators(affiliation: DIRECT) {
                                    totalCount
                                }
                            }
                        }
                    }
                    pageInfo {
                        hasNextPage
                        endCursor
                    }
                }
            }
        """)
        variable_values = {"the_query": the_query, "page_size": page_size,
                           "after_cursor": after_cursor}
        return self.github_client_gql_api.execute(query, variable_values)

    def close_repository_open_issues_with_tag(self, repository: str, tag: str) -> None:
        logging.info(
            f"Closing open issues in repository {repository} with tag {tag}")
        open_issues = self.github_client_core_api.get_repo(f"{self.organisation_name}/{repository}").get_issues(
            state="open")

        open_issues_with_tag = [
            issue
            for issue in open_issues
            for label in issue.labels
            if label.name == tag and issue.state == "open"
        ]

        for issue in open_issues_with_tag:
            logging.info(
                f"Closing issue {issue.title} in repository {issue.repository} because it has tag {tag}")
            issue.edit(state="closed")

    @retries_github_rate_limit_exception_at_next_reset_once
    def get_user_org_email_address(self, user_name) -> str | TypeError:
        logging.info(f"Getting user {user_name} email address")
        data = self.github_client_gql_api.execute(gql("""
            query($organisation_name: String!, $user_name: String!) {
                user(login: $user_name) {
                    organizationVerifiedDomainEmails(login: $organisation_name)
                }
            }
        """), variable_values={"organisation_name": self.organisation_name, "user_name": user_name})

        if data["user"]["organizationVerifiedDomainEmails"]:
            return data["user"]["organizationVerifiedDomainEmails"][0]
        return "-"

    @retries_github_rate_limit_exception_at_next_reset_once
    def get_org_members_login_names(self) -> list[str]:
        logging.info("Getting Org Members Login Names")
        members = self.github_client_core_api.get_organization(
            self.organisation_name).get_members() or []
        return [member.login.lower() for member in members]

    @retries_github_rate_limit_exception_at_next_reset_once
    def _get_user_from_audit_log(self, username: str):
        logging.info("Getting User from Audit Log")
        response_okay = 200
        url = f"https://api.github.com/orgs/{self.organisation_name}/audit-log?phrase=actor%3A{username}"
        response = self.github_client_rest_api.get(url, timeout=10)
        if response.status_code == response_okay:
            return json.loads(response.content.decode("utf-8"))
        return 0

    @retries_github_rate_limit_exception_at_next_reset_once
    def get_audit_log_active_users(self, users: list) -> list:
        three_months_ago_date = datetime.now() - relativedelta(months=3)

        active_users = []
        for user in users:
            audit_log_data = self._get_user_from_audit_log(
                user["username"])
            # No data means the user has no activity in the audit log
            if len(audit_log_data) > 0:
                last_active_date = datetime.fromtimestamp(
                    audit_log_data[0]["@timestamp"] / 1000.0)
                if last_active_date > three_months_ago_date:
                    active_users.append(user["username"].lower())
        return active_users

    @retries_github_rate_limit_exception_at_next_reset_once
    def remove_user_from_gitub(self, user: str):
        github_user = self.github_client_core_api.get_user(user)
        self.github_client_core_api.get_organization(
            self.organisation_name).remove_from_membership(github_user)

    def report_on_inactive_users(self, teams: dict[str, dict[str, Any]], inactivity_months: int, slack_token: str) -> None:
        """
        Reports on inactive users within the given GitHub teams.

        For each team specified in the 'teams' parameter, this method checks the activity status of each user.
        If a user is found to be inactive for a period equal to or greater than 'inactivity_months',
        the user is added to the result list.

        If 'remove_from_team' is set to True for a team in the 'teams' parameter, the inactive user will be removed from the team.

        If slack_channel is provided, a message will be sent to the channel with the list of inactive users.

        Parameters:
            teams (dict[str, dict[str, Any]]): A dictionary containing team configuration.
                Each entry consists of a team name and a dictionary with 'github_team' (team identifier),
                'remove_from_team' (boolean flag to remove inactive users), and any additional team-specific configurations.
            inactivity_months (int): Number of months of inactivity to consider a user as inactive.
            slack_token (str): Slack token to use for sending messages.

        Returns:
            None
        """
        users_to_remove = []
        users_removed = []

        for team_name, team_config in teams.items():
            logging.info(f"Processing team {team_name}")

            github_team = team_config['github_team']
            remove_users = team_config['remove_from_team']
            ignore_users = team_config.get('users_to_ignore', [])
            ignore_repositories = team_config.get('repositories_to_ignore', [])
            slack_channel = team_config.get('slack_channel', None)
            if slack_channel is not None and slack_channel.startswith('#'):
                slack_channel = slack_channel.lstrip('#')

            users = self._get_users_from_team(github_team)
            repositories = self._get_repositories_from_team(github_team)
            if ignore_repositories:
                repositories = [
                    repo for repo in repositories if repo.name not in ignore_repositories]

            for user in users:
                if user.login in ignore_users:
                    logging.info(f"User {user.login} in team {github_team} is ignored")
                    continue
                if self._is_user_inactive(user, inactivity_months, repositories):
                    logging.info(f"User {user.login} in team {github_team} is inactive for {inactivity_months} months")

                    if remove_users:
                        self._remove_user(user, github_team)
                        logging.info(f"User {user.login} removed from team {github_team}")
                        users_removed.append(user)
                    else:
                        users_to_remove.append(user)

            if slack_channel and users_to_remove or slack_channel and users_removed:
                logging.info(f"Sending message to slack channel {slack_channel}")
                SlackService(slack_token).send_message_to_channel(slack_channel, self._message_to_users(users_removed, users_to_remove, github_team))

    def _message_to_users(self, users_removed: list[NamedUser.NamedUser], users_to_remove: list[NamedUser.NamedUser], team_name: str) -> str:
        message = ""
        if users_removed:
            message = f"Users removed from team {team_name}:"
            for user in users_removed:
                message += f"\n- {user.login}"
        if users_to_remove:
            message += f"\n\nUsers identified for removal from team {team_name} but not removed:"
            for user in users_to_remove:
                message += f"\n- {user.login}"

        if message != "":
            message += "\n\n:page_facing_up: Please contact Operations Engineering if you believe this is an error."

        return message

    def _remove_user(self, user: NamedUser.NamedUser, team_name: str) -> None:
        logging.info(f"Removing user {user.login} from team {team_name}")
        try:
            org = self.github_client_core_api.get_organization(self.organisation_name)
            team = org.get_team_by_slug(team_name)

            if team is None:
                logging.warning(f"Team {team_name} not found in organization {self.organisation_name}")
                return

            if not team.has_in_members(user):
                logging.warning(f"User {user.login} is not a member of team {team_name}")
                return

            team.remove_membership(user)
            logging.info(f"User {user.login} removed from team {team_name}")

        except Exception as e:
            logging.error(f"An error occurred while removing user {user.login} from team {team_name}: {str(e)}")

    def _get_users_from_team(self, team_name: str) -> list[NamedUser.NamedUser]:
        org = self.github_client_core_api.get_organization(self.organisation_name)

        for team in org.get_teams():
            if team.name == team_name:
                logging.info(f"Getting users from team {team.name}")
                return list(team.get_members())

        # If the team is not found, return an empty list or handle as needed
        return []

    def _get_repositories_from_team(self, team_name: str) -> list[Repository]:
        org = self.github_client_core_api.get_organization(self.organisation_name)

        for team in org.get_teams():
            if team.name == team_name:
                logging.info(f"Getting repos from team {team.name}")
                return list(team.get_repos())

        logging.warning(f"Team {team_name} not found in organization {self.organisation_name}")
        # If the team is not found, return an empty list or handle as needed
        return []

    def _is_user_inactive(self, user: NamedUser.NamedUser, inactivity_months: int, repositories: list[Repository]) -> bool:
        cutoff_date = datetime.now() - timedelta(days=inactivity_months * 30) # Roughly calculate the cutoff date

        for repo in repositories:
            # Get the user's commits in the repo
            try:
                commits = repo.get_commits(author=user)
            except Exception:
                logging.error(f"An exception occurred while getting commits for user {user.login} in repo {repo.name}")
                continue

            # Check if any commit is later than the cutoff date
            try:
                for commit in commits:
                    if commit.commit.author.date > cutoff_date:
                        return False  # User has been active in this repo, so not considered inactive
            except Exception:
                logging.error(f"An exception occurred while getting commit date for user {user.login} in repo {repo.name}")
                continue

        return True  # User is inactive in all given repositories
