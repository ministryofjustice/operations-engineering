import csv
import logging
import os

import boto3
from botocore.exceptions import NoCredentialsError

from services.dormant_github_user_service import DormantGitHubUser
from services.github_service import GithubService
from services.slack_service import SlackService
from utils.environment import EnvironmentVariables

SLACK_CHANNEL = "operations-engineering-alerts"
AUTH0_DOMAIN = "operations-engineering.eu.auth0.com"
NUMBER_OF_DAYS_CONSIDERED_DORMANT = 90
CSV_FILE_NAME = "dormant.csv"
ORGANISATION = "ministryofjustice"
BUCKET_NAME = "operations-engineering-dormant-users"
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

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def get_usernames_from_csv_ignoring_bots_and_collaborators(bot_list: list) -> list:
    usernames = []
    try:
        with open(CSV_FILE_NAME, mode='r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)

            for row in csv_reader:
                username = row['login'].strip()
                is_collaborator = row['outside_collaborator'].lower() == 'true'
                if username not in bot_list and not is_collaborator:
                    usernames.append(username)

    except FileNotFoundError as e:
        logging.error("Error reading from file %s: %s", CSV_FILE_NAME, e)

    return usernames


def download_github_dormant_users_csv_from_s3():
    s3 = boto3.client('s3')
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
            f"File {CSV_FILE_NAME} not found in the current directory.")


def get_dormant_users_from_github_csv(github_service: GithubService) -> list:
    """
    This function depends on a preliminary manual process: a GitHub Enterprise user must first download the 'dormant.csv'
    file from the GitHub Enterprise dashboard and then upload it to the 'operations-engineering-dormant-users' S3 bucket.
    Once this setup is complete, this function will download the 'dormant.csv' file from the S3 bucket and extract a list of
    usernames from the file. This process ensures that the most current data regarding dormant users is used.
    """
    download_github_dormant_users_csv_from_s3()
    list_of_non_bot_and_non_collaborators = get_usernames_from_csv_ignoring_bots_and_collaborators(
        ALLOWED_BOT_USERS)

    list_of_dormant_users = [DormantGitHubUser(
        github_service, user) for user in list_of_non_bot_and_non_collaborators]

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

    dormant_users_from_csv = get_dormant_users_from_github_csv(
        GithubService(env.get('GH_ADMIN_TOKEN'), ORGANISATION)
    )

    dormant_users_accoding_to_github_and_auth0 = [
        user for user in dormant_users_from_csv if user.is_dormant
    ]

    SlackService(env.get('ADMIN_SLACK_TOKEN')).send_message_to_plaintext_channel_name(
        message_to_slack_channel(
            dormant_users_accoding_to_github_and_auth0), SLACK_CHANNEL
    )


if __name__ == "__main__":
    identify_dormant_github_users()
