import os
import sys
import logging
from requests.exceptions import RequestException

from services.github_service import GithubService
from services.kpi_service import KpiService
from config.constants import ENTERPRISE, MINISTRY_OF_JUSTICE


def get_environment_variables() -> str:
    github_token = os.getenv("GH_TOKEN")
    if not github_token:
        raise ValueError(
            "The env variable GH_TOKEN is empty or missing")

    return github_token


def fetch_gha_quota():
    github_token = get_environment_variables()
    if github_token is None:
        print("No GH_TOKEN environment variable set")
        sys.exit(1)

    github_service = GithubService(github_token, MINISTRY_OF_JUSTICE, ENTERPRISE)

    # get all organisations
    organisations = github_service.get_all_organisations_in_enterprise()
    # get total quota usage
    total_minutes_used = github_service.calculate_total_minutes_used(organisations)

    # save metric in KPI dashboard db
    try:
        KpiService(os.getenv("KPI_DASHBOARD_URL"), os.getenv("KPI_DASHBOARD_API_KEY")).track_enterprise_github_actions_quota_usage(total_minutes_used)
    except RequestException as e:
        logging.info("An error occurred with the database POST request")
        logging.error(e)


if __name__ == "__main__":
    fetch_gha_quota()
