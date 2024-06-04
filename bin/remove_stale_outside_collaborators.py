import pandas as pd
import sys
import os
from gql import gql
from config.logging_config import logging
from services.github_service import GithubService


repo_status_outside_collab_stub = [
    {"name": "r1", "is_repository_open": False, "outside_collaborators":["c1", "c2"]},
    {"name": "r2", "is_repository_open": False, "outside_collaborators":["c2", "c3"]},
    {"name": "r3", "is_repository_open": True, "outside_collaborators":["c1", "c3"]},
    {"name": "r4", "is_repository_open": False, "outside_collaborators":["c2", "c4"]},
    {"name": "r5", "is_repository_open": True, "outside_collaborators":["c1"]},
]


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

# stale_collaborators = extract_stale_outside_collaborators(
#     repo_status_outside_collab_stub
# )

# print(stale_collaborators)

# oauth_token = sys.argv[1]
# github_service = GithubService(oauth_token, "ministryofjustice")

def get_environment_variables() -> str:
    github_token = os.getenv("ADMIN_GITHUB_TOKEN")
    if not github_token:
        raise ValueError(
            "The env variable ADMIN_GITHUB_TOKEN is empty or missing")

    return github_token

# def main():
#     github_token = get_environment_variables()
#     github = GithubService(github_token, "ministryofjustice")

#     data = github.get_paginated_list_of_repos_and_outside_collaborators(
#         after_cursor=None
#     )
#     print(data)
#     return data

def main():
    github_token = get_environment_variables()
    github = GithubService(github_token, "ministryofjustice")

    # data = github.get_org_repo_names()
    # print(data)

    data = github.get_org_unlocked_repo_outside_collaborators()
    print(data)

    return data


if __name__ == "__main__":
    main()
