import os
import sys
from config.constants import ENTERPRISE, MINISTRY_OF_JUSTICE, GITHUB_LICENSE_THRESHOLD
from services.github_service import GithubService
from services.slack_service import SlackService


def alert_on_low_github_licenses():
    github_token = os.environ.get("ADMIN_GITHUB_TOKEN")
    if github_token is None:
        print("No GITHUB_TOKEN environment variable set")
        sys.exit(1)
    slack_token = os.environ.get("ADMIN_SLACK_TOKEN")
    if slack_token is None:
        print("No SLACK_TOKEN environment variable set")
        sys.exit(1)

    remaining_licenses = GithubService(
        github_token, MINISTRY_OF_JUSTICE, ENTERPRISE).get_remaining_licences()
    trigger_alert = remaining_licenses < GITHUB_LICENSE_THRESHOLD

    if trigger_alert:
        print(
            f"Low number of GitHub licenses remaining, only {remaining_licenses} remaining")

        SlackService(slack_token).send_low_github_licenses_alert(remaining_licenses)


if __name__ == "__main__":
    alert_on_low_github_licenses()
