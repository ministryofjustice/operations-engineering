import logging
import os
from dataclasses import dataclass, field
from typing import Optional

import toml
from github.NamedUser import NamedUser

from python.services.github_service import GithubService
from python.services.slack_service import SlackService

config_path = './python/config/inactive-users.toml'
config = toml.load(config_path)

ORGANISATION = config['github']['organisation_name']
INACTIVITY = config['activity_check']['inactivity_months']


@dataclass
class SelfManagedGitHubTeam:
    """
    Represents the configuration for managing a GitHub team within the this service.
    Example features:
        - Remove users from the team if they are not active in any of the team's repositories.
        - Notify a Slack channel when users are removed from the team.

    Attributes:
        github_team (str): The name of the GitHub team.
        remove_users (bool): Flag indicating whether users should be removed from the team.
        ignore_users (list[str]): A list of usernames to ignore when processing the team.
        ignore_repositories (list[str]): A list of repositories to ignore when checking user activity.
        slack_channel (Optional[str]): The Slack channel to notify; None if no notification is needed.

    This class encapsulates the various settings related to a specific GitHub team, such as
    the rules for removing users and the repositories to be ignored. It can be instantiated
    from a TOML configuration file, allowing for easy management of these settings.
    """
    github_team: str
    remove_users: bool = False
    ignore_users: list = field(default_factory=list)
    ignore_repositories: list = field(default_factory=list)
    slack_channel: Optional[str] = None


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


def _message_to_users(users: list[NamedUser], remove: bool, team_name: str, inactivity_months: int) -> str:
    removed_names = "\n".join(
        [f"- {user.login}" for user in users]) if remove else "None"
    to_remove_names = "\n".join(
        [f"- {user.login}" for user in users]) if not remove else "None"

    message = ""
    if removed_names or to_remove_names:
        message = (
            f"Hi team :wave:,\n\n"
            f"As part of our ongoing efforts to maintain the integrity of our GitHub teams, we have analysed user activity for the last {inactivity_months} months. Here's the summary:\n\n"
        )
        if removed_names:
            message += (
                f":outbox_tray: Users Removed:\n{removed_names}\n"
                f"*(These users have been automatically removed from the '{team_name}' team due to inactivity.)*\n\n"
            )
        if to_remove_names:
            message += (
                f":eyes: Users Seen but Not Removed:\n{to_remove_names}\n"
                f"*(These users were identified as inactive in the '{team_name}' team but were not automatically removed. Please review and take appropriate actions.)*\n\n"
            )
        message += (
            "If you have any questions or concerns, please feel free to reach out.\n\n"
            "Best,\nThe Operations Engineering Bot"
        )

    return message


def _load_team_config(team_config: dict) -> SelfManagedGitHubTeam:
    # Ignore the # channel prefix if it exists.
    slack_channel_name = team_config.get('slack_channel', None)
    if slack_channel_name is not None and slack_channel_name.startswith('#'):
        slack_channel_name = slack_channel_name.lstrip('#')

    return SelfManagedGitHubTeam(
        github_team=team_config['github_team'],
        remove_users=team_config['remove_from_team'],
        ignore_users=team_config.get('users_to_ignore', list[str]),
        ignore_repositories=team_config.get(
            'repositories_to_ignore', list[str]),
        slack_channel=slack_channel_name
    )


def main():
    github_token, slack_token = get_environment_variables()
    github = GithubService(github_token, ORGANISATION)
    slack = SlackService(slack_token)

    for team, settings in config['team'].items():
        logging.info(f"Checking for inactive users in team {team}")
        team_data = _load_team_config(settings)

        inactive_users = github.get_inactive_users(
            team_data.github_team, team_data.ignore_users, team_data.ignore_repositories, INACTIVITY)

        if team_data.remove_users:
            github.remove_list_of_users_from_team(
                team_data.github_team, inactive_users)

        if inactive_users and team_data.slack_channel:
            slack.send_message_to_plaintext_channel_name(
                _message_to_users(inactive_users, team_data.remove_users, team, INACTIVITY), team_data.slack_channel)


if __name__ == "__main__":
    main()
