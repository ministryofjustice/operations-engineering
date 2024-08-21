import logging
import os

from services.github_service import GithubService
from services.kpi_service import KpiService


def get_environment_variables() -> str:
    github_token = os.getenv("ADMIN_GITHUB_TOKEN")
    if not github_token:
        raise ValueError("The env variable ADMIN_GITHUB_TOKEN is empty or missing")

    return github_token


def main():
    github_token = get_environment_variables()
    github = GithubService(github_token, "ministryofjustice")

    data = github.get_paginated_list_of_repositories_per_topic(
        topic="standards-compliant", after_cursor=None
    )

    current_repos = [repo_dict["repo"]["name"] for repo_dict in data["search"]["repos"]]

    try:
        KpiService(
            os.getenv("KPI_DASHBOARD_URL"), os.getenv("KPI_DASHBOARD_API_KEY")
        ).track_number_of_repositories_with_standards_label(len(current_repos))
    # pylint: disable=W0718
    except Exception as e:
        logging.info(
            "Issue when trying to track number of repositories with standards label..."
        )
        logging.error(e)

    for repos in current_repos:
        github.set_standards(repository_name=repos)


if __name__ == "__main__":
    main()
