import logging
from dataclasses import dataclass

from services.cloudtrail_service import CloudtrailService
from services.cloudwatch_service import CloudWatchService
from services.github_service import GithubService
from services.slack_service import SlackService
from utils.environment import EnvironmentVariables

SLACK_CHANNEL = "operations-engineering-alerts"
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

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class DormantUser:
    name: str
    email: str


def check_github_for_dormant_users_excluding_bots(
    all_github_users: list, aws_profile: str
) -> list:
    """We export the enterprise audit log from GitHub into AWS Cloudtrail.
    This function will check the cloudtrail logs for the last time a user
    was active on GitHub. If they don't appear in the logs, and aren't a bot,
    as defined above, they are deemed dormant.
    """
    cloudtrail_service = CloudtrailService(aws_profile)
    active_users = cloudtrail_service.get_active_users_for_dormant_users_process()

    return [
        user
        for user in all_github_users
        if user not in list(set(active_users).union(ALLOWED_BOT_USERS))
    ]


def get_active_users_from_auth0_log_group(aws_profile: str) -> list:
    """Operations Engineering, Cloud, Mod and Analytical Platforms all have thir own
    Auth0 tenants. All logs are collected in a single Cloudwatch log group.
    This function will parse the logs and return a list of active users using
    an insights query.
    """
    cloudwatch_log_group = "/aws/events/LogsFromOperationsEngineeringAuth0"

    cloudwatch_service = CloudWatchService(aws_profile, cloudwatch_log_group)
    return cloudwatch_service.get_all_auth0_users_that_appear_in_tenants()


def get_dormant_users_according_to_github_and_auth0(
    github_token, dormant_users_according_to_github: list, aws_profile: str
) -> list:
    active_email_addresses = get_active_users_from_auth0_log_group(aws_profile)
    github_service = GithubService(github_token, ORGANISATION)

    dormant_users = [
        DormantUser(user, github_service.get_user_org_email_address(user))
        for user in dormant_users_according_to_github
    ]

    return [user for user in dormant_users if user.email not in active_email_addresses]


def message_to_slack_channel(list_of_dormant_users: list) -> str:
    msg = (
        "Hello 🤖, \n\n"
        f"The identify dormant GitHub users script has identified {len(list_of_dormant_users)} dormant users. \n-----\n"
    )

    for user in list_of_dormant_users:
        msg += f"{user.name} | Last Github Activity: {user.last_github_activity} | Last Auth0 Activity: {user.last_auth0_activity}\n"

    return msg


def identify_dormant_github_users():
    required_env_vars = [
        "GH_ADMIN_TOKEN",
        "ADMIN_SLACK_TOKEN",
        "MOJDSD_AWS_PROFILE",
        "MODERNISATION_PLATFORM_SANDBOX",
    ]
    env = EnvironmentVariables(required_env_vars)

    all_github_users = GithubService(
        env.get("GH_ADMIN_TOKEN"), ORGANISATION
    ).get_all_enterprise_members()

    dormant_users_according_to_github = check_github_for_dormant_users_excluding_bots(
        all_github_users, env.get("MOJDSD_AWS_PROFILE")
    )

    dormant_users_accoding_to_github_and_auth0 = (
        get_dormant_users_according_to_github_and_auth0(
            env.get("GH_ADMIN_TOKEN"),
            dormant_users_according_to_github,
            env.get("MODRNISATION_PLATFORM_SANDBOX"),
        )
    )
    for user in dormant_users_accoding_to_github_and_auth0:
        logger.info(f"User: {user}")

    logger.info(
        f"Number of users defined dormant: \
        {len(dormant_users_accoding_to_github_and_auth0)}"
    )
    #
    # SlackService(env.get("ADMIN_SLACK_TOKEN")).send_message_to_plaintext_channel_name(
    #     message_to_slack_channel(dormant_users_accoding_to_github_and_auth0),
    #     SLACK_CHANNEL,
    # )


if __name__ == "__main__":
    identify_dormant_github_users()
