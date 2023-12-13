import os
from datetime import datetime, timedelta

from services.github_service import GithubService
from services.slack_service import SlackService


def _calculate_date(in_last_days: int) -> str:
    current_date = datetime.now()
    date = current_date - timedelta(days=in_last_days)
    timestamp_format = "%Y-%m-%d"
    return date.strftime(timestamp_format)


def new_owner_detected_message(new_owner, date_added, added_by, org, audit_log_url):
    msg = (
        f"Hi all, \n\n"
        f"A new owner has been detected in the `{org}` GitHub org. \n\n"
        f"New owner: {new_owner}\n"
        f"Date added: {date_added}\n"
        f"By who: {added_by}\n\n"

        f"Please review the audit log for more details: {audit_log_url}\n\n"


        f"Thanks, \n\n"

        "The GitHub Organisation Monitoring Bot"
    )

    return msg


def check_for_new_organisation_owners(in_last_days: int):
    ORGINISATION = "ministryofjustice"
    SLACK_CHANNEL = "operations-engineering-alerts"

    audit_log_url = f"https://github.com/organizations/{ORGINISATION}/settings/audit-log?q=action%3Aorg.add_member++action%3Aorg.update_member"

    admin_token = os.getenv("ADMIN_GITHUB_TOKEN")
    slack_token = os.getenv("ADMIN_SLACK_TOKEN")
    if not admin_token or not slack_token:
        raise Exception("ADMIN_GITHUB_TOKEN and ADMIN_SLACK_TOKEN must be set")

    gh = GithubService(str(admin_token), ORGINISATION)
    slack = SlackService(str(slack_token))
    changes = gh.flag_owner_permission_changes(_calculate_date(in_last_days))

    if not changes:
        print("No changes detected")

    for change in changes:
        message = new_owner_detected_message(
            change["userLogin"], change["createdAt"], change["actorLogin"], ORGINISATION, audit_log_url)
        slack.send_message_to_plaintext_channel_name(
            message, SLACK_CHANNEL)


if __name__ == "__main__":
    check_for_new_organisation_owners(7)
