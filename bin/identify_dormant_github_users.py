import csv
import logging
import os
from datetime import datetime, timedelta

import boto3
from botocore.exceptions import NoCredentialsError

from services.github_service import GithubService

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


def _calculate_date(in_last_days: int) -> datetime:
    current_date = datetime.now()
    date = current_date - timedelta(days=in_last_days)
    timestamp_format = "%Y-%m-%d"
    return datetime.strptime(date.strftime(timestamp_format), timestamp_format)


def get_usernames_from_csv_ignoring_bots(bot_list: list) -> list:
    usernames = []
    try:
        with open(CSV_FILE_NAME, mode='r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)

            for row in csv_reader:
                username = row[2].strip()
                usernames.append(username)

    except Exception as e:
        print(f"Error reading from file {CSV_FILE_NAME}: {e}")

    return [username for username in usernames if username not in bot_list]


def download_github_dormant_users_csv_from_s3(s3):
    try:
        s3.download_file(BUCKET_NAME, CSV_FILE_NAME, CSV_FILE_NAME)
        logger.info("File %s downloaded successfully.", CSV_FILE_NAME)
    except NoCredentialsError:
        logger.error(
            "Credentials not available, please check your AWS credentials.")
    except Exception as e:
        logger.error("Error downloading file: %s", e)


def setup_environment_variables() -> str:
    github_token = os.environ.get('GH_ADMIN_TOKEN')
    if github_token is None:
        raise ValueError("GITHUB_TOKEN is not set")
    return github_token


def identify_dormant_github_users():
    github_token = setup_environment_variables()
    github_service = GithubService(github_token, ORGANISATION)

    download_github_dormant_users_csv_from_s3(boto3.client('s3'))
    dormant_users = get_usernames_from_csv_ignoring_bots(
        ALLOWED_BOT_USERS)

    dormant_users_not_in_audit_log = github_service.check_dormant_users_activity_since_date(
        dormant_users, _calculate_date(NUMBER_OF_DAYS_CONSIDERED_DORMANT))
    for user in dormant_users_not_in_audit_log:
        print(user)

    logging.info(
        [user for user in dormant_users if user not in dormant_users_not_in_audit_log])


if __name__ == "__main__":
    identify_dormant_github_users()
