import os

import toml

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


def main():
    github_token, slack_token = get_environment_variables()
    teams = {k: v for k, v in config['team'].items()}

    GithubService(github_token, ORGANISATION).report_on_inactive_users(
        teams, INACTIVITY, slack_token)


if __name__ == "__main__":
    main()
