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
        A decorator to retry the method when rate limiting for GitHub resets if the method fails due to RateLimitExceededException.

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

            sleep(time_until_core_api_rate_limit_resets)
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
        return [outside_collaborator.login for outside_collaborator in outside_collaborators]

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

    @retries_github_rate_limit_exception_at_next_reset_once
    def create_an_access_removed_issue_for_user_in_repository(self, user_name: str, repository_name: str) -> None:
        logging.info(
            f"Creating an access removed issue for user {user_name} in repository {repository_name}")
        self.github_client_core_api.get_repo(f"{self.organisation_name}/{repository_name}").create_issue(
            title=self.USER_ACCESS_REMOVED_ISSUE_TITLE,
            assignee=user_name,
            body=dedent(f"""
        Hi there
            
        The user {user_name} had Direct Member access to this repository and access via a team.
             
        Access is now only via a team.
             
        You may have less access it is dependant upon the teams access to the repo.
                   
        If you have any questions, please post in (#ask-operations-engineering)[https://mojdt.slack.com/archives/C01BUKJSZD4] on Slack.
            
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
                                name
                                isDisabled
                                isArchived
                                isLocked
                                hasIssuesEnabled
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
