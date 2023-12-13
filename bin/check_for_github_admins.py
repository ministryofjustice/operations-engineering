import os
from datetime import datetime, timedelta

from services.github_service import GithubService


def _calculate_date(in_last_days: int) -> str:
    current_date = datetime.now()
    date = current_date - timedelta(days=in_last_days)
    timestamp_format = "%Y-%m-%dT%H:%M:%SZ"
    return date.strftime(timestamp_format)


def check_for_new_organisation_owners(in_last_days: int):
    admin_token = os.getenv("ADMIN_GITHUB_TOKEN")
    gh = GithubService(str(admin_token), "ministryofjustice")
    chages = gh.flag_owner_permission_changes(_calculate_date(in_last_days))

    if chages:
        print("New organisation owners found:")
        for change in chages:
            print(f"{change['user']} is now an owner of {change['repo']}")


if __name__ == "__main__":
    check_for_new_organisation_owners(7)
