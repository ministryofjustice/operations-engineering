# get all repositories in poc topic - github service
# get age of all target repositories using gh api - github service
# calculate age of repositories - github service
# compare  to threshold and alert - job level

import sys
import os

from services.github_service import GithubService
from services.slack_service import SlackService
from config.constants import ENTERPRISE, MINISTRY_OF_JUSTICE, SLACK_CHANNEL

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

    print(github_service.get_paginated_list_of_repositories_per_topic("poc"))

if __name__ == "__main__":
    alert_for_old_poc_repositories()
