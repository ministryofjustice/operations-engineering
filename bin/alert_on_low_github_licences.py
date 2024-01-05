"""
GitHub License Monitoring Script

Purpose:
--------
This script monitors the number of available licenses in a GitHub Enterprise account.
It is designed to provide alerts when the license count falls below a
specified threshold.
"""

import os
from config.constants import ENTERPRISE, MINISTRY_OF_JUSTICE, SLACK_CHANNEL
from services.github_service import GithubService
from services.slack_service import SlackService


def low_threshold_triggered_message(remaining_licences):
    msg = (
        f"Hi team 👋, \n\n"
        f"There are only {remaining_licences} \
    GitHub licences remaining in the enterprise account. \n\n"
        f"Please add more licences using the instructions outlined here: \n"
        f"https://runbooks.operations-engineering.service.justice.gov.uk/documentation/internal/low-github-seats-procedure.html \n\n"

        f"Thanks, \n\n"

        "The GitHub Licence Alerting Bot"
    )

    return msg


def alert_on_low_github_licences(threshold=10):
    github_token = os.environ.get("ADMIN_GITHUB_TOKEN")
    if github_token is None:
        print("No GITHUB_TOKEN environment variable set")
        exit(1)
    slack_token = os.environ.get("ADMIN_SLACK_TOKEN")
    if slack_token is None:
        print("No SLACK_TOKEN environment variable set")
        exit(1)

    remaining_licences = GithubService(
        github_token, MINISTRY_OF_JUSTICE, ENTERPRISE).get_remaining_licences()
    trigger_alert = remaining_licences < threshold

    if trigger_alert:
        print(
            f"Low number of GitHub licences remaining, only {remaining_licences} remaining")

        SlackService(slack_token). \
            send_message_to_plaintext_channel_name(
                low_threshold_triggered_message(remaining_licences), SLACK_CHANNEL)


if __name__ == "__main__":
    alert_on_low_github_licences(10)
