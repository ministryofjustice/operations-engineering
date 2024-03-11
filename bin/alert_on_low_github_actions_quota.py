from services.github_service import GithubService
from config.constants import ENTERPRISE, MINISTRY_OF_JUSTICE, SLACK_CHANNEL
import os
import json

def alert_on_low_github_actions_quota():
    github_token = os.environ.get("GH_TOKEN")

    github_service = GithubService(github_token, MINISTRY_OF_JUSTICE, ENTERPRISE)
    
    organisations = github_service.get_all_organisations_in_enterprise()

    for org in organisations:
        billing_data = github_service.get_gha_minutes_used_for_organisation(org.login)
        processed_data = json.loads(billing_data)
        minutes_used = processed_data["total_minutes_used"]
        print(minutes_used)
        
if __name__ == "__main__":
    alert_on_low_github_actions_quota()


