import logging
from calendar import timegm
from datetime import datetime, timedelta
from textwrap import dedent
from time import gmtime, sleep
from typing import Any, Callable

from github import Github, RateLimitExceededException
from github.Issue import Issue
from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
from gql.transport.exceptions import TransportQueryError


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
    GITHUB_GQL_DEFAULT_PAGE_SIZE = 10

    def __init__(self, org_token: str, organisation_name: str) -> None:
        self.github_client_core_api: Github = Github(org_token)
        self.github_client_gql_api: Client = Client(transport=AIOHTTPTransport(
            url="https://api.github.com/graphql",
            headers={"Authorization": f"Bearer {org_token}"},
        ), execute_timeout=60)
        self.organisation_name: str = organisation_name

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

        The user will have been added to an automated generated team named repository-name-<read|write|maintain|admin>-team.

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

    @retries_github_rate_limit_exception_at_next_reset_once
    def add_user_to_team_as_maintainer(self, user_name: str, team_id: int) -> None:
        logging.info(f"Making user {user_name} a maintainer in team {team_id}")
        user = self.github_client_core_api.get_user(user_name)
        self.github_client_core_api.get_organization(
            self.organisation_name).get_team(team_id).add_membership(user, "maintainer")

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
    def get_repository_teams(self, repository_name: str) -> list:
        teams = self.github_client_core_api.get_repo(f"{self.organisation_name}/{repository_name}").get_teams() or []
        return teams

    @retries_github_rate_limit_exception_at_next_reset_once
    def get_repository_direct_users(self, repository_name: str) -> list:
        users = self.github_client_core_api.get_repo(f"{self.organisation_name}/{repository_name}").get_collaborators("direct") or []
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
        variable_values={"the_query": the_query, "page_size": page_size,
                               "after_cursor": after_cursor}
        return self.github_client_gql_api.execute(query, variable_values)
