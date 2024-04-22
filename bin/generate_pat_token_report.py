import os
from datetime import datetime, timedelta
from config.constants import MINISTRY_OF_JUSTICE, SLACK_CHANNEL, OPERATIONS_ENGINEERING_GITHUB_USERNAMES

from services.github_service import GithubService
from services.slack_service import SlackService


def get_environment_variables() -> tuple:
    slack_token = os.getenv("ADMIN_SLACK_TOKEN")
    if not slack_token:
        raise ValueError(
            "The env variable ADMIN_SLACK_TOKEN is empty or missing")
    github_token = os.getenv("GH_APP_TOKEN")
    if not github_token:
        raise ValueError(
            "The env variable GH_APP_TOKEN is empty or missing")

    return slack_token, github_token


def main():
    # audit_log_url = f"https://github.com/organizations/{MINISTRY_OF_JUSTICE}/settings/audit-log?q=action%3Aorg.add_member"
    slack_token, github_token = get_environment_variables()

    github_service = GithubService(str(github_token), MINISTRY_OF_JUSTICE)
    # slack_service = SlackService(str(slack_token))
    new_pat_tokens = github_service.get_new_pat_creation_events_for_organization()

    print(f'Number of PAT tokens found: {len(new_pat_tokens)}')

    # if new_members:
    #     for member in new_members:
    #         individual_message = f"{member['userLogin']} added by {member['actorLogin']}.\n"
    #         if member['actorLogin'] in OPERATIONS_ENGINEERING_GITHUB_USERNAMES:
    #             new_members_added_by_oe += individual_message
    #             total_members_added_by_oe += 1
    #         else:
    #             new_members_added_externally += individual_message
    #     percentage = round((total_members_added_by_oe / len(new_members)) * 100)

    #     slack_service.send_message_to_plaintext_channel_name(new_pat_token_created_message())


if __name__ == "__main__":
    main()
