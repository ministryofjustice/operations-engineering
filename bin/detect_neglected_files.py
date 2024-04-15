import os
import sys
from services.github_service import GithubService
from services.slack_service import SlackService
from config.constants import ENTERPRISE, MINISTRY_OF_JUSTICE, SLACK_CHANNEL


# def low_threshold_triggered_message(percentage_used):
#     return f"Warning:\n\n {round(100 - percentage_used, 1)}% of the Github Actions minutes quota remains.\n\n What to do next: https://runbooks.operations-engineering.service.justice.gov.uk/documentation/internal/low-github-actions-minutes-procedure.html#low-github-actions-minutes-procedure"


def detect_neglected_files():
    github_token = os.environ.get("GH_TOKEN")
    if github_token is None:
        print("No GITHUB_TOKEN environment variable set")
        sys.exit(1)
    # slack_token = os.environ.get("ADMIN_SLACK_TOKEN")
    # if slack_token is None:
    #     print("No SLACK_TOKEN environment variable set")
    #     sys.exit(1)

    github_service = GithubService(github_token, MINISTRY_OF_JUSTICE, ENTERPRISE)
    # slack_service = SlackService(slack_token)

    github_service.detect_neglected_files()


if __name__ == "__main__":
    detect_neglected_files()
