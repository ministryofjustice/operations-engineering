import sys
import os

from services.github_service import GithubService
from services.slack_service import SlackService
from config.constants import ENTERPRISE, MINISTRY_OF_JUSTICE


def alert_for_old_poc_repositories():
    github_token = os.environ.get("GH_TOKEN")
    slack_token = os.environ.get("ADMIN_SLACK_TOKEN")

    if github_token is None:
        print("No GH_TOKEN environment variable set")
        sys.exit(1)

    if slack_token is None:
        print("No ADMIN_SLACK_TOKEN environment variable set")
        sys.exit(1)

    github_service = GithubService(github_token, MINISTRY_OF_JUSTICE, ENTERPRISE)
    slack_service = SlackService(slack_token)

    old_poc_repositories = github_service.get_old_poc_repositories()

    if old_poc_repositories:
        slack_service.send_alert_for_poc_repositories(old_poc_repositories)


if __name__ == "__main__":
    alert_for_old_poc_repositories()
