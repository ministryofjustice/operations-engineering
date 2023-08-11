import os

import toml
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from python.services.github_service import GithubService

config_path = './python/config/inactive-users.toml'
config = toml.load(config_path)

ORGANISATION = config['github']['organisation_name']
INACTIVITY = config['activity_check']['inactivity_months']


def get_environment_variables() -> tuple:
    github_token = os.getenv("ADMIN_GITHUB_TOKEN")
    if not github_token:
        raise ValueError(
            "The env variable ADMIN_GITHUB_TOKEN is empty or missing")

    slack_bot_token = os.getenv("ADMIN_SLACK_TOKEN")
    if not slack_bot_token:
        raise ValueError(
            "The env variable ADMIN_SLACK_TOKEN is empty or missing")

    return github_token, slack_bot_token


def send_message_to_channel(channel_name, message):
    slack_token = os.getenv("ADMIN_SLACK_TOKEN")
    client = WebClient(token=slack_token)

    print(f"Sending message to channel {channel_name}")
    print(f"Using token {slack_token}")

    # Lookup the channel ID by its name
    channel_id = None
    response = client.conversations_list(limit=20)
    while response['response_metadata']['next_cursor'] != '':
        for channel in response['channels']:
            if channel['name'] == channel_name:
                channel_id = channel['id']
                break

        if channel_id is not None:
            break

        response = client.conversations_list(limit=200, cursor=response['response_metadata']['next_cursor'])

    if channel_id is None:
        print(f"Could not find channel {channel_name}")
        return

    # Send the message to the channel
    response = client.chat_postMessage(channel=channel_id, text=message)
    if not response['ok']:
        print(f"Error sending message to channel {channel_name}: {response['error']}")
    else:
        print(f"Message sent to channel {channel_name}")


def main():
    github_token, slack_token = get_environment_variables()
    teams = {k: v for k, v in config['team'].items()}  # Access 'team' sub-dictionary directly

    GithubService(github_token, ORGANISATION).report_on_inactive_users(
        teams, INACTIVITY, slack_token)

if __name__ == "__main__":
    main()

