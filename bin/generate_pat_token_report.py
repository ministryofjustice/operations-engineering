import os
from config.constants import MINISTRY_OF_JUSTICE, SLACK_CHANNEL

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

def expired_tokens_message():
    msg = (
        "Hi team 👋, \n\n"
        "Some expired PAT(s) have been detected. \n\n"
        "Please review the current list here: \n"
        "https://github.com/organizations/ministryofjustice/settings/personal-access-tokens/active \n\n"

        "Have a swell day, \n\n"

        "The GitHub PAT Bot"
    )

    return msg

def count_expired_tokens(pat_tokens):
    expired_count = 0
    for token in pat_tokens:
        if token['token_expired']:
            expired_count += 1
    return expired_count

def main():
    slack_token, github_token = get_environment_variables()

    github_service = GithubService(str(github_token), MINISTRY_OF_JUSTICE)
    slack_service = SlackService(str(slack_token))
    pat_tokens = github_service.get_new_pat_creation_events_for_organization()

    if count_expired_tokens(pat_tokens) > 0:
        slack_service.send_message_to_plaintext_channel_name(expired_tokens_message(), SLACK_CHANNEL)


if __name__ == "__main__":
    main()
