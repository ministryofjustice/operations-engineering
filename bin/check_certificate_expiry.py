import os
import sys
import logging

import boto3
from botocore.exceptions import NoCredentialsError
import json
from json import JSONDecodeError

from services.gandi_service import GandiService
from services.notify_service import NotifyService

from config.constants import MINISTRY_OF_JUSTICE

S3_BUCKET_NAME = "operations-engineering-certificate-email"
S3_OBJECT_NAME = "mappings.json"
CERT_URL_EXTENSION = "v5/certificate/issued-certs"
CERT_REPORT_TEMPLATE_ID = "04b6ca6c-2945-4a0d-a267-53fb61b370ef"
CERT_REPLY_EMAIL = "certificates@digital.justice.gov.uk"

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def get_environment_variables() -> str:
    gandi_token = os.environ.get("GANDI_FUNDS_TOKEN")
    if gandi_token is None:
        print("No GANDI_FUNDS_TOKEN environment variable set")
        sys.exit(1)

    notify_api_key = os.environ.get("NOTIFY_PROD_API_KEY")
    if notify_api_key is None:
        print("No NOTIFY_PROD_API_KEY environment variable set")

    return gandi_token, notify_api_key

def get_json_file_from_s3():
    s3 = boto3.client("s3")
    try:
        with open(S3_OBJECT_NAME, 'wb') as file:
            s3.download_file(S3_BUCKET_NAME, S3_OBJECT_NAME, S3_OBJECT_NAME)
            logger.info("File %s downloaded successfully.", S3_OBJECT_NAME)
        with open(S3_OBJECT_NAME) as file:
            mappings = file.read()
        return json.loads(mappings)

    except NoCredentialsError:
        logger.error(
            "Credentials not available, please check your AWS credentials.")
    except FileNotFoundError as e:
        logger.error("Error downloading file: %s", e)

    except JSONDecodeError as e:
        logger.error("File not in JSON Format: %s", e)


def main(testrun: bool = False, test_email: str = ""):

    # Instantiate services
    logger.info("Instantiating services...")
    gandi_token, notify_api_key = get_environment_variables()
    gandi_service = GandiService(gandi_token, CERT_URL_EXTENSION)
    notify_service = NotifyService("", notify_api_key, MINISTRY_OF_JUSTICE)

    # Get a list of the email mappings from S3
    logger.info("Extracting email map from S3")
    email_mappings = get_json_file_from_s3()

    logger.info("Extracting certificate list from Gandi...")
    certificate_list = gandi_service.get_certificate_list()
    valid_certificate_list = gandi_service.get_certificates_in_valid_state(
        certificate_list, email_mappings)
    if expired_certificate_list := gandi_service.get_expired_certificates_from_valid_certificate_list(
            valid_certificate_list, email_mappings
    ):
        # Build parameters to send emails
        print("Building parameters to send emails...")
        email_parameter_list = notify_service.build_email_parameter_list(
            expired_certificate_list)

        # Send emails for the expired certificates using Notify based on whether it's a test run or not
        if testrun:
            logger.info("Sending test email to {test_email}...")
            notify_service.send_test_email_from_parameters_crs(
                email_parameter_list, test_email)
            logger.info("Building main report...")
            report = notify_service.build_main_report_string_crs(
                email_parameter_list)
            logger.info(f"Sending test report to {test_email}...")
            notify_service.send_report_email_crs(
                report, CERT_REPORT_TEMPLATE_ID, test_email)

        else:
            logger.info("Sending live emails...")
            notify_service.send_emails_from_parameters_crs(email_parameter_list)
            print("Building live report...")
            report = notify_service.build_main_report_string_crs(
                email_parameter_list)
            print("Sending live report to Operations Engineering...")
            notify_service.send_report_email_crs(
                report, CERT_REPORT_TEMPLATE_ID, CERT_REPLY_EMAIL)
    else:
        logger.info("No expiring certificates found.")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        if len(sys.argv) > 2:
            main(True, sys.argv[2])
        else:
            raise SystemExit('Email address of recipient expected.')
    else:
        main()
