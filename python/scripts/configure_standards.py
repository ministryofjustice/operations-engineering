from python.services.github_service import GithubService
import os


def get_environment_variables() -> str:
    github_token = os.getenv("ADMIN_GITHUB_TOKEN")
    if not github_token:
        raise ValueError(
            "The env variable ADMIN_GITHUB_TOKEN is empty or missing")

    return github_token


github_token = get_environment_variables()
github = GithubService(github_token, "ministryofjustice")

data = github.get_paginated_list_of_repositories_per_topic(
    topic="standards-compliant",
    after_cursor=None
)

current_repos = [repo_dict['repo']['name']
                 for repo_dict in data['search']['repos']]

for repos in current_repos:
    github.set_standards(repository_name=repos)
