import os
from datetime import datetime, timedelta

from services.github_service import GithubService

DORMANT_USER_THRESHOLD = 30


def _calculate_date(in_last_days: int) -> str:
    current_date = datetime.now()
    date = current_date - timedelta(days=in_last_days)
    timestamp_format = "%Y-%m-%d"
    return date.strftime(timestamp_format)


def setup_environment() -> tuple[str, str]:
    # get tokens from environment variables
    return "github_token", "auth0_token"


def get_audit_logs() -> list[str]:
    # get github and auth0 audit logs
    return ["user1", "user2", "user3"]


def identify_dormant_users(github_users: list[str], audit_logs: list[str]) -> list[str]:
    # identify users that don't appear in the logs
    return ["user1", "user2", "user3"]


def identify_dormant_github_users():
    github_token = os.getenv("GH_ADMIN_TOKEN")

    github = GithubService(github_token, "ministryofjustice")
    active_github_users = github.get_all_inactive_users_in_enterprise_audit_log_since_date(
        _calculate_date(DORMANT_USER_THRESHOLD))

    # get list of all users from both organisations
    # get github and auth0 audit logs
    # identify users that don't appear in the logs
    # print the users


if __name__ == "__main__":
    identify_dormant_github_users()
