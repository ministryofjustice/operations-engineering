from services.github_service import GithubService
from config.constants import ENTERPRISE, MINISTRY_OF_JUSTICE, SLACK_CHANNEL
import os

def alert_on_low_github_actions_quota():
    github_token = os.environ.get("ADMIN_GITHUB_TOKEN")

    github_service = GithubService(github_token, MINISTRY_OF_JUSTICE, ENTERPRISE)
    
    organisations = github_service.get_all_organisations_in_enterprise()

    for org in organisations:
        print(org)

if __name__ == "__main__":
    alert_on_low_github_actions_quota()


