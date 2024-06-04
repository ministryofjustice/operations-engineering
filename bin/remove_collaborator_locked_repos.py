import sys
import os
import pandas as pd
from gql import gql
from config.logging_config import logging
from services.github_service import GithubService


def get_environment_variables() -> str:
    github_token = os.getenv("ADMIN_GITHUB_TOKEN")
    if not github_token:
        raise ValueError(
            "The env variable ADMIN_GITHUB_TOKEN is empty or missing")

    return github_token


def repository_query(after_cursor=None, repo_name=None) -> gql:
    """A GraphQL query to get the list of outside collaborator in a repo and the locked status
    Args:
        after_cursor (string, optional): Is the pagination offset value gathered from the previous API request. Defaults to None.
        repo_name (string, optional): Is the name of the repository. Defaults to None.
    Returns:
        gql: The GraphQL query result
    """
    query = """
    {
        repository(
            name: REPO_NAME
            owner: "ministryofjustice"
        ) {
            collaborators(first: 100, affiliation: OUTSIDE, after:AFTER) {
                edges {
                    node {
                        login
                    }
                }
                pageInfo {
                    endCursor
                    hasNextPage
                }
            }
            isDisabled
            isArchived
            isLocked
        }
    }
    """.replace(
        # This is the next page ID to start the fetch from
        "AFTER",
        f'"{after_cursor}"' if after_cursor else "null",
    ).replace(
        "REPO_NAME",
        f'"{repo_name}"' if repo_name else "null",
    )

    return gql(query)


def fetch_repository_data(repository_name, github_service: GithubService) -> tuple:
    """A wrapper function to run a GraphQL query to get the list of outside collaborators of a repository and locked status
    Args:
        repository_name (string): Is the repository within the organisation to check
    Returns:
        list: A list of the repository user names
        is_repository_open: Status of the repository
    """
    has_next_page = True
    after_cursor = None
    collaborators_list = []
    is_repository_open = True

    while has_next_page:
        query = repository_query(after_cursor, repository_name)
        data = github_service.github_client_gql_api.execute(query)

        # Retrieve the collaborators
        for repository in data["repository"]["collaborators"]["edges"]:
            collaborators_list.append(repository["node"]["login"])

        # Read the GH API page info section to see if there is more data to read
        has_next_page = data["repository"]["collaborators"]["pageInfo"]["hasNextPage"]
        after_cursor = data["repository"]["collaborators"]["pageInfo"]["endCursor"]

        # Determine lock status
        if (
            data["repository"]["isDisabled"]
            or data["repository"]["isArchived"]
            or data["repository"]["isLocked"]
        ):
            is_repository_open = False

    return collaborators_list, is_repository_open


class Repository:
    """A struct to store repository info ie name, collaborators, locked status"""

    name: str
    collaborators: list
    is_repository_open: bool

    def __init__(self, x, y, z):
        self.name = x
        self.collaborators = y
        self.is_repository_open = z


def fetch_repository_names(github_service: GithubService) -> list:
    """Get the list of repository names in the organisation via REST API
    Returns:
        list: A list of the organisation repository names
    """
    repo_name_list = []

    org = github_service.github_client_core_api.get_organization(
        "ministryofjustice")
    for repo in org.get_repos():
        repo_name_list.append(repo.name)

    return repo_name_list


def fetch_repositories(github_service: GithubService) -> list:
    """Wrapper function to retrieve the repositories info ie name, collaborators, locked status
    Returns:
        list: A list that contains all the repositories data ie name, users, locked status
    """
    repositories_list = []
    for repository_name in fetch_repository_names(github_service):
        collaborators_list, is_repository_open = fetch_repository_data(
            repository_name, github_service
        )
        repositories_list.append(
            Repository(repository_name, collaborators_list,
                       is_repository_open)
        )

    return repositories_list


# def remove_collaborator(collaborator, github_service: GithubService):
#     """Remove the collaborator from the organisation
#     Args:
#         collaborator (collaborator): The collaborator object
#     """
#     logging.info(f"Remove user from organisation: {collaborator.login}")
#     org = github_service.github_client_core_api.get_organization(
#         "ministryofjustice")
#     org.remove_outside_collaborator(collaborator)


def extract_stale_outside_collaborators(
        repo_status_collaborator_list: list[dict]
    ) -> list[str]:
    """
    A function to extract a list of stale collaborators (those not associated with
    any open repositories) from the repository status and outside collaborator list
    of dictionaries.
    """
    df = (
        pd.DataFrame(data = repo_status_collaborator_list)
        .explode("outside_collaborators")
        .groupby("outside_collaborators", as_index=False).sum("is_repository_open")
        .rename(columns={"is_repository_open": "open_repository_count"})
    )
    stale_collaborators = df[df.open_repository_count == 0].outside_collaborators.to_list()
    return stale_collaborators


def run(github_service: GithubService):
    repositories = fetch_repositories(github_service)
    print(repositories)
    stale_outside_collaborators = extract_stale_outside_collaborators(repositories)
    print(stale_outside_collaborators)
    # for collaborator in stale_outside_collaborators:
    #     remove_collaborator(collaborator, github_service)


def main():
    github_token = get_environment_variables()
    github_service = GithubService(github_token, "ministryofjustice")

    run(github_service)


if __name__ == "__main__":
    main()
