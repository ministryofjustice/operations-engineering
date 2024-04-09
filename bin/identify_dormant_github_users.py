import csv
import logging

import boto3
from botocore.exceptions import NoCredentialsError

CSV_FILE_NAME = "dormant.csv"
BUCKET_NAME = "operations-engineering-dormant-users"
BOT_USERS_DEEMED_ACCEPTABLE = [
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


def get_usernames_from_csv(ignored_users: list) -> list:
    usernames = []
    try:
        with open(CSV_FILE_NAME, mode='r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)

            for row in csv_reader:
                username = row[2].strip()
                usernames.append(username)

    except Exception as e:
        print(f"Error reading from file {CSV_FILE_NAME}: {e}")

    return [username for username in usernames if username not in ignored_users]


def download_file_from_s3(file_name):
    s3 = boto3.client('s3')

    try:
        s3.download_file(BUCKET_NAME, CSV_FILE_NAME, file_name)
        print(f"File {file_name} downloaded successfully.")
    except NoCredentialsError:
        print("Credentials not available, please check your AWS credentials.")
    except Exception as e:
        print(f"Error downloading file: {str(e)}")


def identify_dormant_github_users():
    download_file_from_s3(CSV_FILE_NAME)
    dormant_users = get_usernames_from_csv(BOT_USERS_DEEMED_ACCEPTABLE)
    for user in dormant_users:
        print(user)

    print(len(dormant_users))


if __name__ == "__main__":
    identify_dormant_github_users()
