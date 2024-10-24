# get all repositories in poc topic - github service
# get age of all target repositories using gh api - github service
# calculate age of repositories - github service
# compare  to threshold and alert - job level

import sys
import os

from services.github_service import GithubService
from services.slack_service import SlackService
from config.constants import ENTERPRISE, MINISTRY_OF_JUSTICE, SLACK_CHANNEL

def construct_message(percentage_used):
    return f"Warning:\n\n {round(100 - percentage_used, 1)}% of the Github Actions minutes quota remains.\n\n What to do next: https://runbooks.operations-engineering.service.justice.gov.uk/documentation/internal/low-github-actions-minutes-procedure.html#low-github-actions-minutes-procedure"

def alert_for_old_poc_repositories():
    github_token = os.environ.get("GH_TOKEN")
    slack_token = os.environ.get("ADMIN_SLACK_TOKEN")

    if github_token is None:
        print("No GITHUB_TOKEN environment variable set")
        sys.exit(1)

    if slack_token is None:
        print("No SLACK_TOKEN environment variable set")
        sys.exit(1)

    github_service = GithubService(github_token, MINISTRY_OF_JUSTICE, ENTERPRISE)
    slack_service = SlackService(slack_token)

    old_poc_repositories = github_service.get_old_poc_repositories()

    print(old_poc_repositories)

    # if check_result is not False:
    #     slack_service.send_message_to_plaintext_channel_name(construct_message(old_poc_repositories), SLACK_CHANNEL)

if __name__ == "__main__":
    alert_for_old_poc_repositories()
