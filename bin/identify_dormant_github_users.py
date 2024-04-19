import csv
import logging
import os
from datetime import datetime, timedelta

import boto3
from botocore.exceptions import NoCredentialsError

from services.auth0_service import Auth0Service
from services.github_service import GithubService

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
    "sonarqubebot",
    "moj-operations-engineering-bot",
    "operations-engineering-servicenow",
    "laa-service-account",
    "mojanalytics",
    "laaserviceaccount",
]

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


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

    except Exception as e:
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


def get_dormant_users_from_github_csv():
    """An enterprise user must download the 'dormant.csv' file from the Github audit log and upload it to the 'operations-engineering-dormant-users' s3 bucket. This function will download the file from the s3 bucket and return a list of usernames from the csv file."""
    download_github_dormant_users_csv_from_s3()
    return get_usernames_from_csv_ignoring_bots_and_collaborators(ALLOWED_BOT_USERS)


def dormant_users_according_to_github(github_service: GithubService, dormant_from: datetime) -> set[str]:
    usernames_from_csv = get_dormant_users_from_github_csv()
    dormant_users = github_service.check_dormant_users_audit_activity_since_date(
        usernames_from_csv, dormant_from)
    logging.info("Number of dormant users according to Github: %s",
                 len(dormant_users))

    return dormant_users


def dormant_users_not_in_auth0_audit_log(auth0_service: Auth0Service, dormant_users: set[str]) -> set[str]:
    active_users_in_auth0 = auth0_service.get_active_case_sensitive_usernames()

    dormant_users_not_in_audit_log = [
        user for user in dormant_users if user not in active_users_in_auth0]

    return set(dormant_users_not_in_audit_log)


def setup_services() -> tuple[GithubService, Auth0Service]:
    token = os.environ.get('GH_ADMIN_TOKEN')
    if token is None:
        raise ValueError("GH_ADMIN_TOKEN is not set")

    github_service = GithubService(token, ORGANISATION)

    auth0_secret_token = os.environ.get('AUTH0_CLIENT_SECRET')
    auth0_id_token = os.environ.get('AUTH0_CLIENT_ID')
    if auth0_secret_token is None or auth0_id_token is None:
        raise ValueError("AUTH0_SECRET_TOKEN or AUTH0_ID_TOKEN is not set")

    auth0_service = Auth0Service(
        auth0_secret_token, auth0_id_token, AUTH0_DOMAIN
    )

    return github_service, auth0_service


def identify_dormant_github_users():
    since_date = calculate_date_by_integer(NUMBER_OF_DAYS_CONSIDERED_DORMANT)
    github_service, auth0_service = setup_services()

    dormant_users = dormant_users_according_to_github(
        github_service, since_date)
    dormant_users_not_in_auth0 = dormant_users_not_in_auth0_audit_log(
        auth0_service, dormant_users)
    logging.info("Dormant users checked and ready to be removed: %s",
                 dormant_users_not_in_auth0)


if __name__ == "__main__":
    identify_dormant_github_users()
