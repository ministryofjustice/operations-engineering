from datetime import datetime, timedelta
from dataclasses import dataclass
import time
from config.constants import MINISTRY_OF_JUSTICE, MOJ_ANALYTICAL_SERVICES

from services.github_service import GithubService
from services.cloudtrail_service import CloudtrailService
from services.cloudwatch_service import CloudWatchService
from services.slack_service import SlackService
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


@dataclass
class DormantUser:
    name: str
    email: str | None


def get_inactive_users_from_data_lake_ignoring_bots_and_collaborators(github_service, bot_list: list, days_since: int) -> list:
    all_users = github_service.get_all_enterprise_members()

    cloudtrail_service = CloudtrailService()
    active_users = cloudtrail_service.get_active_users_for_dormant_users_process(days_since)

    return [user for user in all_users if user not in list(set(active_users).union(bot_list))]


def filter_out_inactive_committers(gh_orgs, inactive_users_from_audit_log, days_since):

    active_committers = []

    for gh in gh_orgs:
        repos_and_current_contributors = gh.get_current_contributors_for_active_repos()
        since_datetime = (datetime.now() - timedelta(days=days_since))

        for username in inactive_users_from_audit_log:
            commits = False
            if username not in active_committers:
                commits = gh.user_has_commmits_since(
                    username=username,
                    repos_and_contributors=repos_and_current_contributors,
                    since_datetime=since_datetime
                )
            if commits and username not in active_committers:
                active_committers.append(username)

    return list(set(inactive_users_from_audit_log).difference(set(active_committers)))


def get_active_users_from_auth0_log_group(days_since: int) -> list:
    """Operations Engineering, Cloud, Mod and Analytical Platforms all have thir own
    Auth0 tenants. All logs are collected in a single Cloudwatch log group.
    This function will parse the logs and return a list of active users using
    an insights query.
    """
    cloudwatch_log_group = "/aws/events/LogsFromOperationsEngineeringAuth0"

    cloudwatch_service = CloudWatchService(cloudwatch_log_group)
    return cloudwatch_service.get_all_auth0_users_that_appear_in_tenants(days_since)


def filter_out_active_auth0_users(dormant_users_according_to_github: list, days_since: int) -> list:
    active_email_addresses = get_active_users_from_auth0_log_group(days_since)

    dormant_users_not_in_auth0 = [
        user.name
        for user in dormant_users_according_to_github
        if user.email and user.email.lower() not in active_email_addresses
    ]

    return dormant_users_not_in_auth0


def map_usernames_to_emails(users, moj_github_org: GithubService, ap_github_org: GithubService) -> list[DormantUser]:
    dormant_users = [
        DormantUser(
            user,
            moj_github_org.get_user_org_email_address(user)
            or ap_github_org.get_user_org_email_address(user),
        )
        for user in users
    ]

    return dormant_users


def identify_dormant_github_users():
    env = EnvironmentVariables(["GH_MOJ_TOKEN", "GH_MOJAS_TOKEN", "ADMIN_SLACK_TOKEN", "DAYS_SINCE"])
    days_since = int(env.get("DAYS_SINCE"))

    gh_orgs = [
        GithubService(env.get("GH_MOJ_TOKEN"), MINISTRY_OF_JUSTICE),
        GithubService(env.get("GH_MOJAS_TOKEN"), MOJ_ANALYTICAL_SERVICES)
    ]

    dormant_users_according_to_github = get_inactive_users_from_data_lake_ignoring_bots_and_collaborators(
        gh_orgs[0], ALLOWED_BOT_USERS, days_since
    )

    dormant_users_with_emails = map_usernames_to_emails(dormant_users_according_to_github, gh_orgs[0], gh_orgs[1])

    dormant_users_according_to_github_and_auth0 = filter_out_active_auth0_users(dormant_users_with_emails, days_since)

    dormant_users_according_to_github_auth0_and_commits = filter_out_inactive_committers(gh_orgs, dormant_users_according_to_github_and_auth0, days_since)

    SlackService(env.get("ADMIN_SLACK_TOKEN")).send_dormant_user_list(dormant_users_according_to_github_auth0_and_commits, str(days_since))


if __name__ == "__main__":
    start = time.time()
    identify_dormant_github_users()
    end = time.time()
    print(f"\nTime taken: {(end-start) / 60} minutes")
