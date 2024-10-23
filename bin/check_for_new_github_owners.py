import os
from datetime import datetime, timedelta
from config.constants import MINISTRY_OF_JUSTICE

from services.github_service import GithubService
from services.slack_service import SlackService


def _calculate_date(in_last_days: int) -> str:
    current_date = datetime.now()
    date = current_date - timedelta(days=in_last_days)
    timestamp_format = "%Y-%m-%d"
    return date.strftime(timestamp_format)


def check_for_new_organisation_owners(in_last_days: int):
    audit_log_url = f"https://github.com/organizations/{MINISTRY_OF_JUSTICE}/settings/audit-log?q=action%3Aorg.add_member++action%3Aorg.update_member"

    admin_token = os.getenv("ADMIN_GITHUB_TOKEN")
    slack_token = os.getenv("ADMIN_SLACK_TOKEN")
    if not admin_token or not slack_token:
        raise Exception("ADMIN_GITHUB_TOKEN and ADMIN_SLACK_TOKEN must be set")

    gh = GithubService(str(admin_token), MINISTRY_OF_JUSTICE)
    slack = SlackService(str(slack_token))
    changes = gh.flag_owner_permission_changes(_calculate_date(in_last_days))

    if changes:
        for change in changes:
            slack.send_new_github_owners_alert(change["userLogin"], change["createdAt"], change["actorLogin"], MINISTRY_OF_JUSTICE, audit_log_url)


if __name__ == "__main__":
    check_for_new_organisation_owners(7)
