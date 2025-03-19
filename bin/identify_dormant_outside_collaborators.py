from datetime import datetime, timedelta
import logging
import time
import pandas as pd
from config.constants import MINISTRY_OF_JUSTICE, MOJ_ANALYTICAL_SERVICES

from services.github_service import GithubService
from services.slack_service import SlackService
from utils.environment import EnvironmentVariables

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def identify_dormant_outside_collaborators():
    env = EnvironmentVariables(["GH_MOJ_TOKEN", "GH_MOJAS_TOKEN", "ADMIN_SLACK_TOKEN", "DAYS_SINCE"])
    days_since = int(env.get("DAYS_SINCE"))
    since_datetime = (datetime.now() - timedelta(days=days_since))

    gh_orgs = [
        GithubService(env.get("GH_MOJ_TOKEN"), MINISTRY_OF_JUSTICE),
        GithubService(env.get("GH_MOJAS_TOKEN"), MOJ_ANALYTICAL_SERVICES)
    ]

    ocs_repos_and_activity = []
    for gh_org in gh_orgs:
        active_repos_and_outside_collaborators = gh_org.get_active_repos_and_outside_collaborators()
        for repo_object in active_repos_and_outside_collaborators:
            for oc in repo_object.get("outside_collaborators"):
                is_oc_active_in_repo = gh_org.user_has_committed_to_repo_since(
                    username = oc,
                    repo_name = repo_object.get("repository"),
                    since_datetime = since_datetime
                )
                ocs_repos_and_activity.append(
                    {
                        "outside_collaborator": oc,
                        "organisation": gh_org.organisation_name,
                        "repository": repo_object.get("repository"),
                        "public": repo_object.get("public"),
                        "active": is_oc_active_in_repo
                    }
                )

    df_oc_report = pd.DataFrame(ocs_repos_and_activity)
    # Get commit activity for each OC: summing T/F means no commits in any repo shows as 0
    activity_pivot = df_oc_report.pivot_table(['active'], 'outside_collaborator', aggfunc=sum)
    # Filter for zero commits
    zero_commits = activity_pivot.loc[activity_pivot["active"] == 0]

    SlackService(env.get("ADMIN_SLACK_TOKEN")).send_dormant_outside_collaborator_list(
        user_list=zero_commits.index.values,
        days_since=str(days_since)
    )

    return None

if __name__ == "__main__":
    start = time.time()
    identify_dormant_outside_collaborators()
    end = time.time()
    print(f"\nTime taken: {(end-start) / 60} minutes")
