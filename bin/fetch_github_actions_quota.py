import os
import sys
import logging

from services.github_service import GithubService
from services.kpi_service import KpiService
from config.constants import ENTERPRISE, MINISTRY_OF_JUSTICE


def fetch_gha_quota():
    github_token = os.environ.get("GH_TOKEN")
    if github_token is None:
        print("No GITHUB_TOKEN environment variable set")
        sys.exit(1)
    slack_token = os.environ.get("ADMIN_SLACK_TOKEN")
    if slack_token is None:
        print("No SLACK_TOKEN environment variable set")
        sys.exit(1)

    github_service = GithubService(github_token, MINISTRY_OF_JUSTICE, ENTERPRISE)

    # get all organisations
    organisations = github_service.get_all_organisations_in_enterprise()
    # get total quota usage
    total_minutes_used = github_service.calculate_total_minutes_used(organisations)
    # save metric into KPI dashboard database
    try:
        KpiService(os.getenv("KPI_DASHBOARD_URL"), os.getenv("KPI_DASHBOARD_API_KEY")).track_enterprise_github_actions_quota_usage(total_minutes_used)
    except Exception as e:
        logging.info("Issue when trying to track number of repositories with standards label...")
        logging.error(e)


if __name__ == "__main__":
    fetch_gha_quota()
