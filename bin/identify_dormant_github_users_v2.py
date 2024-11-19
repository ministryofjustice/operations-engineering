from datetime import datetime, timedelta
from config.constants import MINISTRY_OF_JUSTICE, MINISTRY_OF_JUSTICE_TEST, MOJ_ANALYTICAL_SERVICES
import time

from services.github_service import GithubService
from services.cloudtrail_service import CloudtrailService
from utils.environment import EnvironmentVariables

# These are the users that are deemed acceptable to be dormant.
# They are either bots or service accounts and will be revisited regularly.
ALLOWED_BOT_USERS = [
    "HmppsDigitalServiceAccount",
    "SonarQubeBot",
    "analytical-platform-bot",
    "ci-hmcts",
    "cloud-platform-dummy-user",
    "correspondence-tool-bot",
    "form-builder-developers",
    "gecko-moj",
    "hmpps-dso-pr-reviewer",
    "hmpps-pcs-tooling",
    "jenkins-moj",
    "laa-machine",
    "laa-service-account",
    "laaserviceaccount",
    "moj-observability-platform-bot",
    "moj-operations-engineering-bot",
    "mojanalytics",
    "mojplatformsdeploy",
    "operations-engineering-servicenow",
    "opg-integrations",
    "opg-use-an-lpa",
    "opg-weblate",
    "slack-moj",
]

def get_inactive_users_from_data_lake_ignoring_bots_and_collaborators(github_service, bot_list: list) -> list:
    all_users = github_service.get_all_enterprise_members()

    cloudtrail_service = CloudtrailService()
    active_users = cloudtrail_service.get_active_users_for_dormant_users_process()

    return [user.lower() for user in all_users if user not in list(set(active_users).union(bot_list))]

def get_inactive_committers(gh_orgs, inactive_users_from_audit_log):

    active_committers = []

    for gh in gh_orgs:
        repos_and_current_contributors = gh.get_current_contributors_for_active_repos()
        since_datetime=(datetime.now() - timedelta(days=90))

        for login in inactive_users_from_audit_log:
            if login not in active_committers:
                commits = gh.user_has_commmits_since(
                    login=login,
                    repos_and_contributors=repos_and_current_contributors,
                    since_datetime=since_datetime
                )
            if commits and login not in active_committers:
                active_committers.append(login)

        return list(set(inactive_users_from_audit_log).difference(set(active_committers)))

def identify_dormant_github_users():
    env = EnvironmentVariables(["GH_ADMIN_TOKEN"])

    gh_orgs = [
        GithubService(env.get("GH_ADMIN_TOKEN"), MINISTRY_OF_JUSTICE),
        GithubService(env.get("GH_ADMIN_TOKEN"), MOJ_ANALYTICAL_SERVICES)
    ]

    dormant_users_according_to_github = get_inactive_users_from_data_lake_ignoring_bots_and_collaborators(gh_orgs[0], ALLOWED_BOT_USERS)

    dormant_users_accoding_to_github_and_commit_activity = get_inactive_committers(gh_orgs, dormant_users_according_to_github)

    print(dormant_users_accoding_to_github_and_commit_activity)

    print(len(dormant_users_accoding_to_github_and_commit_activity))


if __name__ == "__main__":
    start = time.time()
    identify_dormant_github_users()
    end = time.time()
    print(f"\nTime taken: {(end-start) / 60} minutes")
