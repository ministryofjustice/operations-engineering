import os
import sys
from services.github_service import GithubService
from services.slack_service import SlackService
from config.constants import ENTERPRISE, MINISTRY_OF_JUSTICE, SLACK_CHANNEL


def construct_neglected_files_slack_blocks(paths_to_review: str, organisation: str, repo: str):
    urlified_paths = [f"https://github.com/{organisation}/{repo}/blob/main/" + path for path in paths_to_review]
    return [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"The following paths in the {repo} repository are due for review:\n\n" + "\n".join(urlified_paths)
                    }
                }
            ]


def detect_neglected_files():
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

    repo = "operations-engineering"

    paths_to_review = github_service.detect_neglected_files_in_multiple_directories(repo, ["bin"])

    if len(paths_to_review) > 1:
        slack_service._send_alert_to_operations_engineering(construct_neglected_files_slack_blocks(paths_to_review, "ministryofjustice", repo))


if __name__ == "__main__":
    detect_neglected_files()
