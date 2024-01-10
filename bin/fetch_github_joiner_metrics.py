import os
from datetime import datetime, timedelta
from config.constants import MINISTRY_OF_JUSTICE, SLACK_CHANNEL

from services.github_service import GithubService
from services.slack_service import SlackService

def get_environment_variables() -> tuple:
    slack_token = os.getenv("ADMIN_SLACK_TOKEN")
    if not slack_token:
        raise ValueError(
            "The env variable ADMIN_SLACK_TOKEN is empty or missing")
    github_token = os.getenv("ADMIN_GITHUB_TOKEN")
    if not github_token:
        raise ValueError(
            "The env variable ADMIN_GITHUB_TOKEN is empty or missing")

    return slack_token, github_token


def _calculate_date(in_last_days: int) -> str:
    current_date = datetime.now()
    date = current_date - timedelta(days=in_last_days)
    timestamp_format = "%Y-%m-%d"
    return date.strftime(timestamp_format)

def new_members_detected_message(new_members, org, audit_log_url, time_delta_in_days):
    msg = (
        f"Hi all, \n\n"
        f"Here are the members added in the last {time_delta_in_days} days within the '{org}' GitHub org. \n\n"
        f"{new_members}\n\n"
        f"Please review the audit log for more details: {audit_log_url}\n\n"
        f"Have a swell day, \n\n"
        "The GitHub Organisation Monitoring Bot"
    )

    return msg

def main():
    audit_log_url = f"https://github.com/organizations/{MINISTRY_OF_JUSTICE}/settings/audit-log?q=action%3Aorg.add_member"

    time_delta_in_days = 7
    slack_token, github_token = get_environment_variables()

    github_service = GithubService(str(github_token), MINISTRY_OF_JUSTICE)
    slack_service = SlackService(str(slack_token))
    new_members = github_service.check_for_audit_log_new_members(_calculate_date(time_delta_in_days))
    full_member_list = ""

    if new_members:
        for member in new_members:
            print(f"New member detected: {member['userLogin']}")
            individual_message = f"*New member:* {member['userLogin']} added by {member['actorLogin']}.\n"
            full_member_list.append(individual_message)

        slack_service.send_message_to_plaintext_channel_name(
            new_members_detected_message(full_member_list, MINISTRY_OF_JUSTICE, audit_log_url, time_delta_in_days), SLACK_CHANNEL)


if __name__ == "__main__":
    main()

