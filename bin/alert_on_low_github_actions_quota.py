import os
import sys
from services.github_service import GithubService
from services.slack_service import SlackService
from config.constants import ENTERPRISE, MINISTRY_OF_JUSTICE


def alert_on_low_quota():
    github_token = os.environ.get("GH_TOKEN")
    if github_token is None:
        print("No GITHUB_TOKEN environment variable set")
        sys.exit(1)
    slack_token = os.environ.get("ADMIN_SLACK_TOKEN")
    if slack_token is None:
        print("No SLACK_TOKEN environment variable set")
        sys.exit(1)

    github_service = GithubService(github_token, MINISTRY_OF_JUSTICE, ENTERPRISE)
    slack_service = SlackService(slack_token)

    check_result = github_service.check_if_gha_minutes_quota_is_low()

    if check_result is not False:
        slack_service.send_low_github_actions_quota_alert(check_result['percentage_used'])
        github_service.modify_gha_minutes_quota_threshold(check_result['threshold'] + 10)


if __name__ == "__main__":
    alert_on_low_quota()
