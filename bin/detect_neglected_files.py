import os
import sys
from services.github_service import GithubService
from services.slack_service import SlackService
from config.constants import ENTERPRISE, MINISTRY_OF_JUSTICE, SLACK_CHANNEL


def construct_neglected_files_slack_message(paths_to_review: str, organisation: str, repo: str):
    hyperlinkified_paths = [f"<https://github.com/{organisation}/{repo}/blob/main/{path}|{path}>" for path in paths_to_review]
    return f"The following paths in the <https://github.com/{organisation}/{repo}|{repo}> repository are due for review:\n\n" + "\n".join(hyperlinkified_paths)

def detect_neglected_files():
    github_token = os.environ.get("GH_TOKEN")
    if github_token is None:
        print("No GITHUB_TOKEN environment variable set")
        sys.exit(1)
    slack_token = os.environ.get("SLACK_TOKEN")
    if slack_token is None:
        print("No SLACK_TOKEN environment variable set")
        sys.exit(1)

    github_service = GithubService(github_token, MINISTRY_OF_JUSTICE, ENTERPRISE)
    slack_service = SlackService(slack_token)

    repo = "operations-engineering"

    paths_to_review = github_service.detect_neglected_files_in_multiple_directories(repo, ["bin"])

    if len(paths_to_review) > 1:
        slack_service.send_message_to_plaintext_channel_name(construct_neglected_files_slack_message(paths_to_review, "ministryofjustice", repo), SLACK_CHANNEL)


if __name__ == "__main__":
    detect_neglected_files()
