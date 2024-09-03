import csv
import logging
import os
from dataclasses import dataclass
from datetime import datetime

import boto3
from botocore.exceptions import NoCredentialsError

from services.cloudwatch_service import CloudWatchService
from services.github_service import GithubService
from services.slack_service import SlackService
from utils.environment import EnvironmentVariables

BUCKET_NAME = "operations-engineering-identify-dormant-github-user-csv"
CSV_FILE_NAME = "dormant.csv"
MOJ_ORGANISATION = "ministryofjustice"
AP_ORGANISATION = "moj-analytical-services"
SLACK_CHANNEL = "operations-engineering-alerts"
# These are the users that are deemed acceptable to be dormant.
# They are either bots or service accounts and will be revisited regularly.
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
    email: str | None


def get_usernames_from_csv_ignoring_bots_and_collaborators(bot_list: list) -> list:
    usernames = []
    try:
        with open(CSV_FILE_NAME, mode="r", encoding="utf-8") as file:
            csv_reader = csv.DictReader(file)

            for row in csv_reader:
                username = row["login"].strip()
                is_collaborator = row["outside_collaborator"].lower() == "true"
                if username not in bot_list and not is_collaborator:
                    usernames.append(username)

    except FileNotFoundError as e:
        logging.error("Error reading from file %s: %s", CSV_FILE_NAME, e)

    return usernames


def download_github_dormant_users_csv_from_s3():
    s3 = boto3.client("s3")
    try:
        s3.download_file(BUCKET_NAME, CSV_FILE_NAME, CSV_FILE_NAME)
        logger.info("File %s downloaded successfully.", CSV_FILE_NAME)
    except NoCredentialsError:
        logger.error(
            "Credentials not available, please check your AWS credentials.")
    except FileNotFoundError as e:
        logger.error("Error downloading file: %s", e)

    if not os.path.isfile(CSV_FILE_NAME):
        raise FileNotFoundError(
            f"File {CSV_FILE_NAME} not found in the current directory."
        )


def get_dormant_users_from_github_csv(
    moj_github_org: GithubService, ap_github_org: GithubService
) -> list[DormantUser]:
    """
    This function depends on a preliminary manual process: a GitHub Enterprise user
    must first download the 'dormant.csv' file from the GitHub Enterprise dashboard and
    then upload it to an S3 bucket. Once this setup is complete, this function will
    download the 'dormant.csv' file from the S3 bucket and extract a list of
    usernames from the file.

    This process ensures that the most current data regarding dormant users is used.
    """
    download_github_dormant_users_csv_from_s3()
    users = get_usernames_from_csv_ignoring_bots_and_collaborators(
        ALLOWED_BOT_USERS)

    dormant_users = [
        DormantUser(
            user,
            moj_github_org.get_user_org_email_address(user)
            or ap_github_org.get_user_org_email_address(user),
        )
        for user in users
    ]

    return dormant_users


def get_active_users_from_auth0_log_group() -> list:
    """Operations Engineering, Cloud, Mod and Analytical Platforms all have thir own
    Auth0 tenants. All logs are collected in a single Cloudwatch log group.
    This function will parse the logs and return a list of active users using
    an insights query.
    """
    cloudwatch_log_group = "/aws/events/LogsFromOperationsEngineeringAuth0"

    cloudwatch_service = CloudWatchService(cloudwatch_log_group)
    return cloudwatch_service.get_all_auth0_users_that_appear_in_tenants()


def filter_out_active_auth0_users(dormant_users_according_to_github: list) -> list:
    active_email_addresses = get_active_users_from_auth0_log_group()

    dormant_users_not_in_auth0 = [
        user
        for user in dormant_users_according_to_github
        if user.email and user.email.lower() not in active_email_addresses
    ]
    return dormant_users_not_in_auth0

def message_to_slack_channel(dormant_users: list) -> str:
    msg = "Hello 🤖,\n\n"
    msg += "Here is a list of dormant GitHub users that have not been seen in Auth0 logs in the last 90 days:\n\n"

    msg += "\n".join(f"- {user.name} | {user.email}" for user in dormant_users)

    return msg

def message_to_slack_channel(dormant_users: list) -> str:
    msg = (
        "Hello 🤖, \n\n"
        "Here is a list of dormant GitHub users that have not been seen in Auth0 logs:\n\n"
    )

    for user in dormant_users:
        msg += f"GitHub username: {user.name} | Email: {user.email}\n"

    return msg


def save_dormant_users_to_csv(dormant_users: list[DormantUser]):
    current_date = datetime.now().strftime("%Y-%m-%d")
    output_csv_file_name = f"{current_date}_dormant_users.csv"

    with open(output_csv_file_name, mode="w", newline="", encoding="utf-8") as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(["Name", "Email"])
        for user in dormant_users:
            csv_writer.writerow([user.name, user.email])

    logger.info("Dormant users have been written to %s",
                {output_csv_file_name})


def identify_dormant_github_users():
    required_env_vars = [
        "GH_MOJ_ADMIN_TOKEN",
        "GH_AP_ADMIN_TOKEN",
        "ADMIN_SLACK_TOKEN",
    ]
    env = EnvironmentVariables(required_env_vars)

    # To identify email addresses, we need to check both
    # the MOJ and AP GitHub organisations as there is no enterprise opion for this.
    moj_github_org = GithubService(env.get(
        "GH_MOJ_ADMIN_TOKEN"), MOJ_ORGANISATION)
    ap_github_org = GithubService(env.get(
        "GH_AP_ADMIN_TOKEN"), AP_ORGANISATION)

    githubs_list_of_dormant_users = get_dormant_users_from_github_csv(
        moj_github_org, ap_github_org)

    dormant_users_accoding_to_github_and_auth0 = filter_out_active_auth0_users(
        githubs_list_of_dormant_users
    )

    SlackService(env.get("ADMIN_SLACK_TOKEN")).send_message_to_plaintext_channel_name(
        message_to_slack_channel(dormant_users_accoding_to_github_and_auth0),
        SLACK_CHANNEL,
    )


if __name__ == "__main__":
    identify_dormant_github_users()
