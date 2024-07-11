import logging

from services.dormant_github_user_service import DormantGitHubUser
from services.github_service import GithubService
from services.slack_service import SlackService
from services.cloudtrail_service import CloudtrailService
from utils.environment import EnvironmentVariables

SLACK_CHANNEL = "operations-engineering-alerts"
AUTH0_DOMAIN = "operations-engineering.eu.auth0.com"
ORGANISATION = "ministryofjustice"
# These are the users that are deemed acceptable to be dormant. They are either bots or service accounts and will be revisited regularly.
ALLOWED_BOT_USERS = [
    "ci-hmcts",
    "cloud-platform-dummy-user",
    "correspondence-tool-bot",
    "form-builder-developers",
    "gecko-moj",
    "hmpps-pcs-tooling",
    "jenkins-moj",
    "laa-machine",
    "mojplatformsdeploy",
    "opg-integrations",
    "opg-use-an-lpa",
    "opg-weblate",
    "slack-moj",
    "SonarQubeBot",
    "moj-operations-engineering-bot",
    "operations-engineering-servicenow",
    "laa-service-account",
    "mojanalytics",
    "laaserviceaccount",
]

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def get_inactive_users_from_data_lake_ignoring_bots_and_collaborators(github_service, bot_list: list) -> list:
    all_users = github_service.get_all_enterprise_members()

    cloudtrail_service = CloudtrailService()
    active_users = cloudtrail_service.get_active_users_for_dormant_users_process()

    return [user for user in all_users if user not in list(set(active_users).union(bot_list))]


def get_dormant_users_from_data_lake(github_service: GithubService) -> list:
    list_of_inactive_github_users = get_inactive_users_from_data_lake_ignoring_bots_and_collaborators(github_service, ALLOWED_BOT_USERS)

    list_of_dormant_users = [DormantGitHubUser(github_service, user) for user in list_of_inactive_github_users]

    return list_of_dormant_users


def message_to_slack_channel(list_of_dormant_users: list) -> str:
    msg = (
        "Hello 🤖, \n\n"
        f"The identify dormant GitHub users script has identified {len(list_of_dormant_users)} dormant users. \n-----\n"
    )

    # Add each dormant user on a new line
    for user in list_of_dormant_users:
        msg += f"{user.name} | Last Github Activity: {user.last_github_activity} | Last Auth0 Activity: {user.last_auth0_activity}\n"

    return msg


def identify_dormant_github_users():
    env = EnvironmentVariables(["GH_ADMIN_TOKEN", "ADMIN_SLACK_TOKEN"])

    dormant_users_according_to_github = get_dormant_users_from_data_lake(GithubService(env.get('GH_ADMIN_TOKEN'), ORGANISATION))

    dormant_users_accoding_to_github_and_auth0 = [user for user in dormant_users_according_to_github if user.is_dormant]

    SlackService(env.get('ADMIN_SLACK_TOKEN')).send_message_to_plaintext_channel_name(message_to_slack_channel(dormant_users_accoding_to_github_and_auth0), SLACK_CHANNEL)


if __name__ == "__main__":
    identify_dormant_github_users()
