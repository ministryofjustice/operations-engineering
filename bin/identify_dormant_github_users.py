import csv
import logging
import os
from dataclasses import dataclass
from datetime import datetime, timedelta

import boto3
from botocore.exceptions import NoCredentialsError

from services.auth0_service import Auth0Service
from services.dormant_github_user import DormantGitHubUser
from services.github_service import GithubService
from services.slack_service import SlackService

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


@dataclass
class DormantUserEnvironment:
    github_token: str = os.environ.get('GH_ADMIN_TOKEN', "")
    auth0_secret_token: str = os.environ.get('AUTH0_CLIENT_SECRET', "")
    auth0_id_token: str = os.environ.get('AUTH0_CLIENT_ID', "")
    slack_token: str = os.environ.get('ADMIN_SLACK_TOKEN', "")

    def __post_init__(self):
        if not self.github_token:
            raise ValueError("GH_ADMIN_TOKEN is not set")
        if not self.auth0_secret_token or not self.auth0_id_token:
            raise ValueError(
                "AUTH0_CLIENT_SECRET or AUTH0_CLIENT_ID is not set")


def calculate_date_by_integer(in_last_days: int) -> datetime:
    current_date = datetime.now()
    date = current_date - timedelta(days=in_last_days)
    timestamp_format = "%Y-%m-%d"
    return datetime.strptime(date.strftime(timestamp_format), timestamp_format)


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
    except Exception as e:
        logger.error("Error downloading file: %s", e)

    if not os.path.isfile(CSV_FILE_NAME):
        raise FileNotFoundError(
            f"File {CSV_FILE_NAME} not found in the current directory.")


def get_dormant_users_from_github_csv(github_service: GithubService) -> list:
    """An enterprise user must download the 'dormant.csv' file from the Github audit log and upload it to the 'operations-engineering-dormant-users' s3 bucket. This function will download the file from the s3 bucket and return a list of usernames from the csv file."""
    list_of_dormant_users = []
    download_github_dormant_users_csv_from_s3()
    list_of_non_bot_and_non_collaborators = get_usernames_from_csv_ignoring_bots_and_collaborators(
        ALLOWED_BOT_USERS)

    for user in list_of_non_bot_and_non_collaborators:
        list_of_dormant_users.append(DormantGitHubUser(github_service, user))

    return list_of_dormant_users


def message_to_slack_channel(list_of_dormant_users: set) -> str:
    msg = (
        "Hi team 👋, \n\n"
        f"The identify dormant GitHub users script has identified {len(list_of_dormant_users)} dormant users. \n\n"
    )

    # Add each dormant user on a new line
    for user in list_of_dormant_users:
        msg += f"{user}\n"

    return msg


def identify_dormant_github_users():
    dormant_since_date = calculate_date_by_integer(
        NUMBER_OF_DAYS_CONSIDERED_DORMANT)
    env = DormantUserEnvironment()

    list_of_dormant_users_from_csv = get_dormant_users_from_github_csv(
        GithubService(env.github_token, ORGANISATION))

    for user in list_of_dormant_users_from_csv:
        print("User:", user.name, "Last Auth0 Activity:",
              user.email, "Last Github Activity:", user.last_github_activity, "Last Auth0 Activity:", user.last_auth0_activity)


if __name__ == "__main__":
    identify_dormant_github_users()
