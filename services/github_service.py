# pylint: disable=E1136, E1135, W0718, C0411

import json
from calendar import timegm
from datetime import date, datetime, timedelta, timezone
from time import gmtime, sleep
from typing import Any, Callable

from dateutil.relativedelta import relativedelta
from github import (Github, NamedUser, RateLimitExceededException,
                    UnknownObjectException, GithubException)
from github.Organization import Organization
from github.Repository import Repository
from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
from gql.transport.exceptions import TransportServerError
from requests import Session

from config.logging_config import logging

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
        except (RateLimitExceededException, TransportServerError) as exception:
            logging.warning(
                f"Caught {type(exception).__name__}, retrying calls when rate limit resets.")
            rate_limits = args[0].github_client_core_api.get_rate_limit()
            rate_limit_to_use = rate_limits.core if isinstance(
                exception, RateLimitExceededException) else rate_limits.graphql

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
    ENTERPRISE_NAME = "ministry-of-justice-uk"

    # Added to stop TypeError on instantiation. See https://github.com/python/cpython/blob/d2340ef25721b6a72d45d4508c672c4be38c67d3/Objects/typeobject.c#L4444
    def __new__(cls, *_, **__):
        return super(GithubService, cls).__new__(cls)

    def __init__(self, org_token: str, organisation_name: str,
                 enterprise_name: str = ENTERPRISE_NAME) -> None:
        self.organisation_name: str = organisation_name
        self.enterprise_name: str = enterprise_name
        self.organisations_in_enterprise: list = ["ministryofjustice", "moj-analytical-services"]

        self.github_client_core_api: Github = Github(org_token)
        self.github_client_gql_api: Client = Client(transport=AIOHTTPTransport(
            url="https://api.github.com/graphql",
            headers={"Authorization": f"Bearer {org_token}"},
        ), execute_timeout=120)
        self.github_client_rest_api = Session()
        self.github_client_rest_api.headers.update(
            {
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {org_token}",
            }
        )

    @retries_github_rate_limit_exception_at_next_reset_once
    def get_outside_collaborators_login_names(self) -> list[str]:
        logging.info("Getting Outside Collaborators Login Names")
        outside_collaborators = self.github_client_core_api.get_organization(
            self.organisation_name).get_outside_collaborators() or []
        return [outside_collaborator.login.lower() for outside_collaborator in outside_collaborators]

    @retries_github_rate_limit_exception_at_next_reset_once
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
        logging.info(f"Adding user {user.login} to team {team_id}")
        try:
            self.github_client_core_api.get_organization(self.organisation_name).get_team(team_id).add_membership(user)
        except GithubException as err:
            print(f"Could not add {user.login} to team {team_id}: {err}")

    @retries_github_rate_limit_exception_at_next_reset_once
    def __get_repositories_from_team(self, team_id: int) -> list[Repository]:
        logging.info(f"Getting all repositories for team {team_id}")
        return self.github_client_core_api.get_organization(self.organisation_name).get_team(
            team_id).get_repos() or []

    @retries_github_rate_limit_exception_at_next_reset_once
    def __get_users_from_team(self, team_id: int) -> list:
        logging.info(f"Getting all named users for team {team_id}")
        return self.github_client_core_api.get_organization(self.organisation_name).get_team(
            team_id).get_members() or []

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
    def get_paginated_list_of_org_repository_names(self, after_cursor: str | None,
                                                   page_size: int = GITHUB_GQL_DEFAULT_PAGE_SIZE) -> dict[str, Any]:
        logging.info(
            f"Getting paginated list of org repository names. Page size {page_size}, after cursor {bool(after_cursor)}")
        if page_size > self.GITHUB_GQL_MAX_PAGE_SIZE:
            raise ValueError(
                f"Page size of {page_size} is too large. Max page size {self.GITHUB_GQL_MAX_PAGE_SIZE}")
        return self.github_client_gql_api.execute(gql("""
            query($organisation_name: String!, $page_size: Int!, $after_cursor: String) {
                organization(login: $organisation_name) {
                    repositories(first: $page_size, after: $after_cursor, isLocked: false, isArchived: false) {
                        pageInfo {
                            endCursor
                            hasNextPage
                        }
                        edges {
                            node {
                                isDisabled
                                name
                            }
                        }
                    }
                }
            }
        """), variable_values={"organisation_name": self.organisation_name, "page_size": page_size,
                               "after_cursor": after_cursor})

    @retries_github_rate_limit_exception_at_next_reset_once
    def get_paginated_list_of_unlocked_unarchived_repos_and_their_first_100_outside_collaborators(
        self,
        after_cursor: str | None,
        page_size: int = GITHUB_GQL_DEFAULT_PAGE_SIZE,
    ) -> dict[str, Any]:
        logging.info(
            f"Getting paginated list of org unlocked unarchived repositories and their first 100 outside collaborators. Page size {page_size}, after cursor {bool(after_cursor)}"
        )
        if page_size > self.GITHUB_GQL_MAX_PAGE_SIZE:
            raise ValueError(
                f"Page size of {page_size} is too large. Max page size {self.GITHUB_GQL_MAX_PAGE_SIZE}")
        return self.github_client_gql_api.execute(gql("""
            query($organisation_name: String!, $page_size: Int!, $after_cursor: String) {
                organization(login: $organisation_name) {
                    repositories(first: $page_size, after: $after_cursor, isLocked: false, isArchived: false) {
                        pageInfo {
                            endCursor
                            hasNextPage
                        }
                        nodes {
                            name
                            isDisabled
                            collaborators(first: 100, affiliation: OUTSIDE){
                                pageInfo {
                                    hasNextPage
                                }
                                edges {
                                    node {
                                        login
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
    def get_paginated_list_of_repositories_per_type(self, repo_type: str, after_cursor: str | None,
                                                    page_size: int = GITHUB_GQL_DEFAULT_PAGE_SIZE) -> dict[str, Any]:
        logging.info(
            f"Getting paginated list of repositories per type {repo_type}. Page size {page_size}, after cursor {bool(after_cursor)}")
        if page_size > self.GITHUB_GQL_MAX_PAGE_SIZE:
            raise ValueError(
                f"Page size of {page_size} is too large. Max page size {self.GITHUB_GQL_MAX_PAGE_SIZE}")
        the_query = f"org:{self.organisation_name}, archived:false, is:{repo_type}"
        return self.github_client_gql_api.execute(gql("""
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
                                isDisabled
                                isPrivate
                                isLocked
                                name
                                pushedAt
                                url
                                description
                                hasIssuesEnabled
                                repositoryTopics(first: 10) {
                                    edges {
                                        node {
                                            topic {
                                                name
                                            }
                                        }
                                    }
                                }
                                defaultBranchRef {
                                    name
                                }
                                collaborators(affiliation: DIRECT) {
                                    totalCount
                                }
                                licenseInfo {
                                    name
                                }
                                collaborators(affiliation: DIRECT) {
                                    totalCount
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
                    pageInfo {
                        hasNextPage
                        endCursor
                    }
                }
            }
        """), variable_values={"the_query": the_query, "page_size": page_size, "after_cursor": after_cursor})

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
    def get_team_names(self) -> list[str]:
        """A wrapper function to run a GraphQL query to get the team names in the organisation

        Returns:
            list: A list of the team names
        """
        has_next_page = True
        after_cursor = None
        team_names = []

        while has_next_page:
            data = self.get_paginated_list_of_team_names(after_cursor, 100)

            if data["organization"]["teams"]["edges"] is not None:
                for team in data["organization"]["teams"]["edges"]:
                    team_names.append(team["node"]["slug"])

            has_next_page = data["organization"]["teams"]["pageInfo"]["hasNextPage"]
            after_cursor = data["organization"]["teams"]["pageInfo"]["endCursor"]
        return team_names

    @retries_github_rate_limit_exception_at_next_reset_once
    def get_team_repository_names(self, team_name: str) -> list[str]:
        """A wrapper function to run a GraphQL query to get a team repository names

        Returns:
            list: A list of the team repository names
        """
        has_next_page = True
        after_cursor = None
        team_repository_names = []

        while has_next_page:
            data = self.get_paginated_list_of_team_repositories(
                team_name, after_cursor, 100)

            if data["organization"]["team"]["repositories"]["edges"] is not None:
                for team in data["organization"]["team"]["repositories"]["edges"]:
                    team_repository_names.append(team["node"]["name"])

            has_next_page = data["organization"]["team"]["repositories"]["pageInfo"]["hasNextPage"]
            after_cursor = data["organization"]["team"]["repositories"]["pageInfo"]["endCursor"]
        return team_repository_names

    @retries_github_rate_limit_exception_at_next_reset_once
    def get_team_user_names(self, team_name: str) -> list[str]:
        """A wrapper function to run a GraphQL query to get a team user names

        Returns:
            list: A list of the team user names
        """
        has_next_page = True
        after_cursor = None
        team_user_names = []

        while has_next_page:
            data = self.get_paginated_list_of_team_user_names(
                team_name, after_cursor, 100)

            if data["organization"]["team"]["members"]["edges"] is not None:
                for team in data["organization"]["team"]["members"]["edges"]:
                    team_user_names.append(team["node"]["login"])

            has_next_page = data["organization"]["team"]["members"]["pageInfo"]["hasNextPage"]
            after_cursor = data["organization"]["team"]["members"]["pageInfo"]["endCursor"]
        return team_user_names

    @retries_github_rate_limit_exception_at_next_reset_once
    def get_org_repo_names(self) -> list[str]:
        """A wrapper function to run a GraphQL query to get a list of the organisation repository names
        (open repositories only).

        Returns:
            list: A list of the organisation repository names
        """
        has_next_page = True
        after_cursor = None
        repository_names = []
        while has_next_page:
            data = self.get_paginated_list_of_org_repository_names(
                after_cursor, 100)

            if data["organization"]["repositories"]["edges"] is not None:
                for repo in data["organization"]["repositories"]["edges"]:
                    if repo["node"]["isDisabled"]:
                        continue
                    repository_names.append(repo["node"]["name"])

            has_next_page = data["organization"]["repositories"]["pageInfo"]["hasNextPage"]
            after_cursor = data["organization"]["repositories"]["pageInfo"]["endCursor"]
        return repository_names

    @retries_github_rate_limit_exception_at_next_reset_once
    def check_circleci_config_in_repos(self) -> list[str]:
        """Check if each repository in the list has a CircleCI configuration file using GraphQL.

        Args:
            repo_list (list): A list of repository names.

        Returns:
            list: A list of repository names that have a CircleCI configuration file.
        """
        has_next_page = True
        after_cursor = None
        repos_with_circleci_config = []

        while has_next_page:
            data = self.get_paginated_circleci_config_check(after_cursor, 100)

            if data["organization"]["repositories"]["edges"]:
                for repo in data["organization"]["repositories"]["edges"]:
                    if repo["node"]["object"]:
                        repos_with_circleci_config.append(repo["node"]["name"])

            has_next_page = data["organization"]["repositories"]["pageInfo"]["hasNextPage"]
            after_cursor = data["organization"]["repositories"]["pageInfo"]["endCursor"]
        return repos_with_circleci_config

    def get_paginated_circleci_config_check(self, after_cursor: str | None, page_size: int) -> dict[str, Any]:
        logging.info(f"Checking CircleCI config in repos. Page size {page_size}, after cursor {bool(after_cursor)}")
        if page_size > self.GITHUB_GQL_MAX_PAGE_SIZE:
            raise ValueError(f"Page size of {page_size} is too large. Max page size {self.GITHUB_GQL_MAX_PAGE_SIZE}")

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
                            object(expression: "HEAD:.circleci/config.yml") {
                                ... on Blob {
                                    id
                                }
                            }
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

    def get_stale_outside_collaborators(self) -> list[str]:
        """A wrapper function to run a GraphQL query to get a list of the Stale Outside Collaborators
        in the organisation. These are Outside Collaborators not affiliated with any open (not locked,
        not archived nor disabled) repositories. The function collects the Active Outside Collaborators
        (those affiliated with at least one open repository) and then subtracts these from the total
        list of Outside Collaborators.

        Returns:
            list: A list of the organisation stale outside collaborators login names in lower case
        """

        all_outside_collaborators = self.get_outside_collaborators_login_names()
        repo_has_next_page = True
        after_cursor = None
        active_outside_collaborators = []
        while repo_has_next_page:
            data = self.get_paginated_list_of_unlocked_unarchived_repos_and_their_first_100_outside_collaborators(
                after_cursor, self.GITHUB_GQL_MAX_PAGE_SIZE
            )
            if data["organization"]["repositories"]["nodes"] is not None:
                for repo in data["organization"]["repositories"]["nodes"]:
                    if repo["isDisabled"]:
                        continue
                    # The query only returns the first 100 Outside Collaborators on a repo, if there is a next page
                    # it will not collect them. This is very unlikely to occur, however the function output is
                    # unreliable if it does so.
                    if repo["collaborators"]["pageInfo"]["hasNextPage"]:
                        raise ValueError(
                            "Some Outside Collaborators omitted from calculation; cannot get reliable Stale Outside Collaborators list."
                        )
                    for collaborators in repo["collaborators"]["edges"]:
                        if collaborators:
                            active_outside_collaborators.append(collaborators["node"]["login"].lower())
            repo_has_next_page = data["organization"]["repositories"]["pageInfo"]["hasNextPage"]
            after_cursor = data["organization"]["repositories"]["pageInfo"]["endCursor"]

        stale_outside_collaborators = set(all_outside_collaborators) - set(active_outside_collaborators)

        return list(stale_outside_collaborators)

    @retries_github_rate_limit_exception_at_next_reset_once
    def fetch_all_repositories_in_org(self) -> list[dict[str, Any]]:
        """A wrapper function to run a GraphQL query to get the list of repositories in the organisation

        Returns:
            list: A list of the organisation repos names
        """
        repos = []

        # Specifically switch off logging for this query as it is very large and doesn't need to be logged
        logging.disabled = True

        for repo_type in ["public", "private", "internal"]:
            after_cursor = None
            has_next_page = True
            while has_next_page:
                data = self.get_paginated_list_of_repositories_per_type(
                    repo_type, after_cursor)

                if data["search"]["repos"] is not None:
                    for repo in data["search"]["repos"]:
                        if repo["repo"]["isDisabled"] or repo["repo"]["isLocked"]:
                            continue
                        repos.append(repo["repo"])

                has_next_page = data["search"]["pageInfo"]["hasNextPage"]
                after_cursor = data["search"]["pageInfo"]["endCursor"]

        # Re-enable logging
        logging.disabled = False
        return repos

    @retries_github_rate_limit_exception_at_next_reset_once
    def get_paginated_list_of_team_user_names(self, team_name: str, after_cursor: str | None,
                                              page_size: int = GITHUB_GQL_DEFAULT_PAGE_SIZE) -> dict[str, Any]:

        logging.info(
            f"Getting paginated list of team user names. Page size {page_size}, after cursor {bool(after_cursor)}")
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
    def get_repository_direct_users(self, repository_name: str) -> list:
        users = self.github_client_core_api.get_repo(
            f"{self.organisation_name}/{repository_name}").get_collaborators("direct") or []
        return [member.login.lower() for member in users]

    @retries_github_rate_limit_exception_at_next_reset_once
    def get_repository_collaborators(self, repository_name: str) -> list:
        users = self.github_client_core_api.get_repo(
            f"{self.organisation_name}/{repository_name}").get_collaborators("outside") or []
        return [member.login.lower() for member in users]

    @retries_github_rate_limit_exception_at_next_reset_once
    def get_paginated_list_of_repositories_per_topic(self, topic: str, after_cursor: str | None,
                                                     page_size: int = GITHUB_GQL_DEFAULT_PAGE_SIZE) -> dict[str, Any]:
        """
        Fetches a paginated list of repositories associated with a given GitHub topic/

        Parameters:
        - topic (str): The GitHub topic for which to fetch associated repositories.
        - after_cursor (str | None): The pagination cursor to fetch results after a certain point. If None, fetches from the beginning.
        - page_size (int, optional): The number of repository results to return per page. Defaults to GITHUB_GQL_DEFAULT_PAGE_SIZE.
            Note that there's an upper limit, GITHUB_GQL_MAX_PAGE_SIZE, beyond which an exception will be raised.

        Returns:
        - dict[str, Any]: A dictionary containing the repository data and pagination information.

        Raises:
        - ValueError: If the specified page size exceeds GitHub's maximum allowable page size.

        Usage:
        >>> get_paginated_list_of_repositories_per_topic('standards-compliant', None, 50)
        { ...repository data... }

        """
        logging.info(
            f"Getting paginated list of repositories per topic {topic}. Page size {page_size}, after cursor {bool(after_cursor)}")
        if page_size > self.GITHUB_GQL_MAX_PAGE_SIZE:
            raise ValueError(
                f"Page size of {page_size} is too large. Max page size {self.GITHUB_GQL_MAX_PAGE_SIZE}")
        the_query = f"org:{self.organisation_name}, archived:false, topic:{topic}"
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
                                repositoryTopics(first: 10) {
                                    edges {
                                        node {
                                            topic {
                                                name
                                            }
                                        }
                                    }
                                }
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

    @retries_github_rate_limit_exception_at_next_reset_once
    def get_user_org_email_address(self, user_name) -> str | None:
        data = self.github_client_gql_api.execute(gql("""
            query($organisation_name: String!, $user_name: String!) {
                user(login: $user_name) {
                    organizationVerifiedDomainEmails(login: $organisation_name)
                }
            }
        """), variable_values={"organisation_name": self.organisation_name, "user_name": user_name})

        if data["user"]["organizationVerifiedDomainEmails"]:
            return data["user"]["organizationVerifiedDomainEmails"][0]
        return None

    @retries_github_rate_limit_exception_at_next_reset_once
    def get_org_members_login_names(self) -> list[str]:
        logging.info("Getting Org Members Login Names")
        members = self.github_client_core_api.get_organization(
            self.organisation_name).get_members() or []
        return [member.login.lower() for member in members]

    def enterprise_audit_activity_for_user(self, username: str):
        response_okay = 200
        url = f"https://api.github.com/enterprises/{self.enterprise_name}/audit-log?phrase=actor%3A{username}"
        response = self.github_client_rest_api.get(url, timeout=10)
        if response.status_code == response_okay:
            return json.loads(response.content.decode("utf-8"))
        raise ValueError(
            f"Failed to get audit activity for user {username}. Response status code: {response.status_code}")

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

    def get_last_audit_log_activity_date_for_user(self, username: str) -> datetime | None:
        audit_activity = self.enterprise_audit_activity_for_user(username)
        if audit_activity:
            return datetime.fromtimestamp(audit_activity[0]["@timestamp"] / 1000.0)
        return None

    @retries_github_rate_limit_exception_at_next_reset_once
    def check_dormant_users_audit_activity_since_date(self, users: list, since_date: datetime) -> list:
        return [user for user in users if self.is_user_dormant_since_date(user, since_date)]

    def is_user_dormant_since_date(self, user: str, since_date: datetime) -> bool:
        audit_activity = self.enterprise_audit_activity_for_user(user)
        if audit_activity:
            last_active_date = datetime.fromtimestamp(
                audit_activity[0]["@timestamp"] / 1000.0)
            if last_active_date < since_date:
                logging.info(
                    f"User {user} last active date: {last_active_date}, adding to dormant users list")
                return True
        else:
            logging.info(
                f"User {user} has no audit activity, adding to dormant users list")
            return True
        return False

    @retries_github_rate_limit_exception_at_next_reset_once
    def remove_user_from_gitub(self, user: str):
        github_user = self.github_client_core_api.get_user(user)
        self.github_client_core_api.get_organization(
            self.organisation_name).remove_from_membership(github_user)

    @retries_github_rate_limit_exception_at_next_reset_once
    def remove_outside_collaborator_from_org(self, outside_collaborator: str):
        github_user = self.github_client_core_api.get_user(outside_collaborator)
        self.github_client_core_api.get_organization(
            self.organisation_name
        ).remove_outside_collaborator(
            github_user
        )

    def get_inactive_users(self, team_name: str, users_to_ignore, repositories_to_ignore: list[str],
                           inactivity_months: int) -> list[NamedUser.NamedUser]:
        """
        Identifies and returns a list of inactive users from a specified GitHub team based on a given inactivity period.

            :param team_name: The name of the GitHub team to check for inactive users.
            :type team_name: str
            :param users_to_ignore: A list of usernames to ignore during the inactivity check.
            :type users_to_ignore: list[str]
            :param repositories_to_ignore: A list of repository names to exclude from the inactivity check.
            :type repositories_to_ignore: list[str]
            :param inactivity_months: The threshold for user inactivity, specified in months. Users inactive for longer than this period are considered inactive.
            :type inactivity_months: int
            :return: A list of NamedUser objects representing the users who are identified as inactive.
            :rtype: list[NamedUser.NamedUser]

        Example Usage:
            inactive_users = get_inactive_users("operations-engineering", ["user1"], ["repo1"], 18)
        """
        team_id = self.get_team_id_from_team_name(team_name)
        logging.info(
            f"Identifying inactive users in team {team_name}, id = {team_id}")
        users = self._get_unignored_users_from_team(team_id, users_to_ignore)
        repositories = self._get_repositories_managed_by_team(
            team_id, repositories_to_ignore)
        return self._identify_inactive_users(users, repositories, inactivity_months)

    def _identify_inactive_users(self, users: list[NamedUser.NamedUser], repositories: list[Repository],
                                 inactivity_months: int) -> list[NamedUser.NamedUser]:
        users_to_remove = []
        for user in users:
            if self._is_user_inactive(user, repositories, inactivity_months):
                logging.info(
                    f"User {user.login} is inactive for {inactivity_months} months")
                users_to_remove.append(user)
        return users_to_remove

    def _get_unignored_users_from_team(self, team_id: int, users_to_ignore: list[str]) -> list[NamedUser.NamedUser]:
        logging.info(f"Ignoring users {users_to_ignore}")
        users = self.__get_users_from_team(team_id)
        return [user for user in users if user.login not in users_to_ignore]

    def _get_repositories_managed_by_team(self, team_id: int, repositories_to_ignore: list[str]) -> list[Repository]:
        logging.info(f"Ignoring repositories {repositories_to_ignore}")
        repositories = self.__get_repositories_from_team(team_id)
        return [repo for repo in repositories if repo.name.lower() not in repositories_to_ignore]

    def _is_user_inactive(self, user: NamedUser.NamedUser, repositories: list[Repository],
                          inactivity_months: int) -> bool:
        cutoff_date = datetime.now() - timedelta(days=inactivity_months *
                                                 30)  # Roughly calculate the cutoff date

        for repo in repositories:
            # Get the user's commits in the repo
            try:
                commits = repo.get_commits(author=user)
            except Exception:
                logging.error(
                    f"An exception occurred while getting commits for user {user.login} in repo {repo.name}")
                continue

            # Check if any commit is later than the cutoff date
            try:
                for commit in commits:
                    if commit.commit.author.date > cutoff_date:
                        return False  # User has been active in this repo, so not considered inactive
            except Exception:
                logging.error(
                    f"An exception occurred while getting commit date for user {user.login} in repo {repo.name}")
                continue

        return True  # User is inactive in all given repositories

    @retries_github_rate_limit_exception_at_next_reset_once
    def _get_paginated_organization_members_with_emails(self, after_cursor: str | None,
                                                        page_size: int = GITHUB_GQL_MAX_PAGE_SIZE) -> dict[str, Any]:
        logging.info(
            f"Getting paginated organization members with emails. Page size {page_size}, after cursor {bool(after_cursor)}")

        if page_size > self.GITHUB_GQL_MAX_PAGE_SIZE:
            raise ValueError(
                f"Page size of {page_size} is too large. Max page size {self.GITHUB_GQL_MAX_PAGE_SIZE}")

        query = gql("""
            query($org: String!, $page_size: Int!, $after_cursor: String) {
                organization(login: $org) {
                    membersWithRole(first: $page_size, after: $after_cursor) {
                        nodes {
                            login
                            organizationVerifiedDomainEmails(login: $org)
                        }
                        pageInfo {
                            hasNextPage
                            endCursor
                        }
                    }
                }
            }
        """)

        variable_values = {
            "org": self.organisation_name,
            "page_size": page_size,
            "after_cursor": after_cursor
        }

        return self.github_client_gql_api.execute(query, variable_values)

    def get_github_member_list(self):
        github_usernames = []
        next_page = True
        after_cursor = None
        all_members = []

        while next_page:
            response = self._get_paginated_organization_members_with_emails(
                after_cursor=after_cursor)

            if 'errors' in response:
                logging.error(
                    f"Error retrieving organization members: {response['errors']}")
                break

            if 'organization' in response and 'membersWithRole' in response['organization']:
                all_members = response['organization']['membersWithRole']['nodes']
                member_data = response['organization']['membersWithRole']

                for member in all_members:
                    email = member['organizationVerifiedDomainEmails'][0] if member[
                        'organizationVerifiedDomainEmails'] else None
                    github_usernames.append({
                        "username": member["login"],
                        "email": email
                    })
                next_page = member_data['pageInfo']['hasNextPage']
                if next_page:
                    after_cursor = member_data['pageInfo']['endCursor']
            else:
                next_page = False

        return github_usernames

    def get_remaining_licences(self) -> int:
        """
        Fetches the number of remaining licenses in the GitHub Enterprise.

        Returns:
            int: The number of remaining licenses.
        """
        licence = self.github_client_core_api.get_enterprise(
            self.enterprise_name).get_consumed_licenses()
        return licence.total_seats_purchased - licence.total_seats_consumed

    @retries_github_rate_limit_exception_at_next_reset_once
    def update_team_repository_permission(self, team_name: str, repositories, permission: str):
        org = self.github_client_core_api.get_organization(
            self.organisation_name)

        try:
            team = org.get_team_by_slug(team_name)
        except UnknownObjectException as exc:
            raise ValueError(
                f"Team '{team_name}' does not exist in organization '{self.organisation_name}'") from exc

        for repo_name in repositories:
            try:
                repo = org.get_repo(repo_name)
            except UnknownObjectException as exc:
                raise ValueError(
                    f"Repository '{repo_name}' does not exist in organization '{self.organisation_name}'") from exc

            logging.info(
                f"Updating {team_name} team's permission to {permission} on {repo_name}")
            team.set_repo_permission(repo, permission)

    def flag_owner_permission_changes(self, since_date: str) -> list:
        recent_changes = self.audit_log_member_changes(since_date)
        list_of_changes_to_flag = []
        for change in recent_changes:
            match change["action"]:
                case "org.add_member" if change["permission"] == "ADMIN":
                    list_of_changes_to_flag.append(change)
                case "org.update_member" if change["permission"] == "ADMIN" and change["permissionWas"] == "READ":
                    list_of_changes_to_flag.append(change)
                case _:
                    logging.info(
                        f"Change {change} does not meet criteria to flag")

        return list_of_changes_to_flag

    @retries_github_rate_limit_exception_at_next_reset_once
    def audit_log_member_changes(self, since_date: str) -> list:
        logging.info(f"Getting audit log entries since {since_date}")
        today = datetime.now()
        query = """
            query($organisation_name: String!, $since_date: String!, $cursor: String) {
                organization(login: $organisation_name) {
                    auditLog(
                        first: 100
                        after: $cursor
                        query: $since_date
                    ) {
                        edges{
                            node{
                                ... on OrgAddMemberAuditEntry {
                                    action
                                    createdAt
                                    actorLogin
                                    operationType
                                    permission
                                    userLogin
                                }
                                ... on OrgUpdateMemberAuditEntry {
                                    action
                                    createdAt
                                    actorLogin
                                    operationType
                                    permission
                                    permissionWas
                                    userLogin
                                }
                            }
                        }
                        pageInfo {
                            endCursor
                            hasNextPage
                        }
                    }
                }
            }
        """
        variable_values = {
            "organisation_name": self.organisation_name,
            "since_date": f"action:org.add_member  action:org.update_member  created:{since_date}..{today.strftime('%Y-%m-%d')}",
            "cursor": None
        }

        all_entries = []
        while True:
            data = self.github_client_gql_api.execute(
                gql(query), variable_values=variable_values)
            all_entries.extend(
                [entry["node"] for entry in data["organization"]["auditLog"]["edges"] if entry["node"]])

            if data["organization"]["auditLog"]["pageInfo"]["hasNextPage"]:
                variable_values["cursor"] = data["organization"]["auditLog"]["pageInfo"]["endCursor"]
            else:
                break

        return all_entries

    @retries_github_rate_limit_exception_at_next_reset_once
    def check_for_audit_log_new_members(self, since_date: str) -> list:
        logging.info(
            f"Getting audit log entries for new members since {since_date}")
        today = datetime.now()
        query = """
            query($organisation_name: String!, $since_date: String!, $cursor: String) {
                organization(login: $organisation_name) {
                    auditLog(
                        first: 100
                        after: $cursor
                        query: $since_date
                    ) {
                        edges{
                            node{
                                ... on OrgAddMemberAuditEntry {
                                    action
                                    createdAt
                                    actorLogin
                                    userLogin
                                }
                            }
                        }
                        pageInfo {
                            endCursor
                            hasNextPage
                        }
                    }
                }
            }
        """
        variable_values = {
            "organisation_name": self.organisation_name,
            "since_date": f"action:org.add_member created:{since_date}..{today.strftime('%Y-%m-%d')}",
            "cursor": None
        }

        new_members = []
        while True:
            data = self.github_client_gql_api.execute(
                gql(query), variable_values=variable_values)
            new_members.extend(
                [entry["node"] for entry in data["organization"]["auditLog"]["edges"] if entry["node"]])

            if data["organization"]["auditLog"]["pageInfo"]["hasNextPage"]:
                variable_values["cursor"] = data["organization"]["auditLog"]["pageInfo"]["endCursor"]
            else:
                break

        return new_members

    @retries_github_rate_limit_exception_at_next_reset_once
    def get_all_organisations_in_enterprise(self) -> list[Organization]:
        logging.info(
            f"Getting all organisations for enterprise {self.ENTERPRISE_NAME}")

        return [org.login for org in self.github_client_core_api.get_user().get_orgs()] or []

    @retries_github_rate_limit_exception_at_next_reset_once
    def get_gha_minutes_used_for_organisation(self, organization) -> int:
        logging.info(
            f"Getting all github actions minutes used for organization {organization}")

        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }

        response = self.github_client_rest_api.get(
            f"https://api.github.com/orgs/{organization}/settings/billing/actions", headers=headers)

        return response.json()

    @retries_github_rate_limit_exception_at_next_reset_once
    def modify_gha_minutes_quota_threshold(self, new_threshold):
        logging.info(f"Changing the alerting threshold to {new_threshold}%")

        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }

        payload = {'value': str(new_threshold)}

        self.github_client_rest_api.patch(
            "https://api.github.com/repos/ministryofjustice/operations-engineering/actions/variables/GHA_MINUTES_QUOTA_THRESHOLD", json.dumps(payload), headers=headers)

    @retries_github_rate_limit_exception_at_next_reset_once
    def _get_repository_variable(self, variable_name):
        actions_variable = self.github_client_core_api.get_repo(
            f'{self.organisation_name}/operations-engineering').get_variable(variable_name)
        return actions_variable.value

    @retries_github_rate_limit_exception_at_next_reset_once
    def reset_alerting_threshold_if_first_day_of_month(self):
        base_alerting_threshold = int(self._get_repository_variable("GHA_MINUTES_QUOTA_BASE_THRESHOLD"))

        if date.today().day == 1:
            self.modify_gha_minutes_quota_threshold(base_alerting_threshold)

    @retries_github_rate_limit_exception_at_next_reset_once
    def calculate_total_minutes_used(self, organisations):
        total = 0

        for org in organisations:
            billing_data = self.get_gha_minutes_used_for_organisation(org)
            minutes_used = billing_data["total_minutes_used"]
            total += minutes_used

        return total

    @retries_github_rate_limit_exception_at_next_reset_once
    def check_if_gha_minutes_quota_is_low(self):
        organisations = self.get_all_organisations_in_enterprise()

        total_minutes_used = self.calculate_total_minutes_used(organisations)

        print(f"Total minutes used: {total_minutes_used}")

        total_quota = int(self._get_repository_variable("GHA_MINUTES_QUOTA_TOTAL"))

        percentage_used = (total_minutes_used / total_quota) * 100

        self.reset_alerting_threshold_if_first_day_of_month()

        threshold = int(self._get_repository_variable("GHA_MINUTES_QUOTA_THRESHOLD"))

        if percentage_used >= threshold:
            return {'threshold': threshold, 'percentage_used': percentage_used}
        return False

    @retries_github_rate_limit_exception_at_next_reset_once
    def get_new_pat_creation_events_for_organization(self) -> list:
        logging.info(
            f"Fetching PATs for the {self.organisation_name} organisation...")

        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }

        url = f"https://api.github.com/orgs/{self.organisation_name}/personal-access-tokens"

        response = self.github_client_rest_api.get(url, headers=headers)

        if response.status_code == 200:
            logging.info("Successfully retrieved PAT list.")
            return response.json()

        raise ValueError(f"Failed to fetch PAT list: {response.status_code}, error: {response}")

    @retries_github_rate_limit_exception_at_next_reset_once
    def get_all_enterprise_members(self) -> list:
        all_users = []

        for org in self.organisations_in_enterprise:
            all_users = all_users + [user.login for user in self.github_client_core_api.get_organization(org).get_members() if user.login not in all_users]

        return all_users

    @retries_github_rate_limit_exception_at_next_reset_once
    def calculate_repo_age(self, repo: str) -> list:
        creation_date = self.github_client_core_api.get_repo(f"{self.organisation_name}/{repo}").created_at

        age_in_days = (datetime.now(timezone.utc) - creation_date).days

        return age_in_days

    @retries_github_rate_limit_exception_at_next_reset_once
    def get_old_poc_repositories(self) -> list:
        poc_repositories = [repo['repo']['name'] for repo in self.get_paginated_list_of_repositories_per_topic("poc", None)['search']['repos']]

        old_poc_repositories = {}
        age_threshold = 30

        for repo in poc_repositories:
            age = self.calculate_repo_age(repo)
            if age >= age_threshold:
                old_poc_repositories[repo] = age

        return old_poc_repositories

    @retries_github_rate_limit_exception_at_next_reset_once
    def get_user_removal_events(self, since_date: str, actor: str) -> list:
        logging.info(f"Getting audit log entries for users removed by {actor} since {since_date}")
        today = datetime.now()
        query_string = f"action:org.remove_member actor:{actor} created:{since_date}..{today.strftime('%Y-%m-%d')}"

        query = """
            query($organisation_name: String!, $query_string: String!, $cursor: String) {
                organization(login: $organisation_name) {
                    auditLog(
                        first: 100
                        after: $cursor
                        query: $query_string
                    ) {
                        edges{
                            node{
                                ... on OrgRemoveMemberAuditEntry {
                                    action
                                    createdAt
                                    actorLogin
                                    userLogin
                                }
                            }
                        }
                        pageInfo {
                            endCursor
                            hasNextPage
                        }
                    }
                }
            }
        """
        variable_values = {
            "organisation_name": self.organisation_name,
            "query_string": query_string,
            "cursor": None
        }

        removed_users = []
        while True:
            data = self.github_client_gql_api.execute(
                gql(query), variable_values=variable_values)
            removed_users.extend(
                [entry["node"] for entry in data["organization"]["auditLog"]["edges"] if entry["node"]])
            if data["organization"]["auditLog"]["pageInfo"]["hasNextPage"]:
                variable_values["cursor"] = data["organization"]["auditLog"]["pageInfo"]["endCursor"]
            else:
                break

        return removed_users
