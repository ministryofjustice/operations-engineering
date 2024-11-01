import os
import sys
import logging

import boto3
from botocore.exceptions import NoCredentialsError
import json
from json import JSONDecodeError

from services.gandi_service import GandiService
from services.notify_service import NotifyService
from services.s3_service import S3Service

from config.constants import MINISTRY_OF_JUSTICE


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


cert_config = {
    "CERT_REPLY_EMAIL": "certificates@digital.justice.gov.uk",
    "CERT_EXPIRY_THRESHOLDS": [30],
    "CERT_URL_EXTENSION": "v5/certificate/issued-certs",
    "CERT_REPORT_TEMPLATE_ID": "04b6ca6c-2945-4a0d-a267-53fb61b370ef",
    "CERT_EXPIRY_TEMPALATE_ID": "06abd028-0a8f-43d9-a122-90a92f9b62ee"
}


def get_environment_variables() -> tuple:
    gandi_token = os.environ.get("GANDI_CERTIFICATES_TOKEN")
    if not gandi_token:
        raise ValueError("No GANDI_CERTIFICATES_TOKEN environment variable set")

    notify_api_key = os.environ.get("NOTIFY_PROD_API_KEY")
    if not notify_api_key:
        raise ValueError("No NOTIFY_PROD_API_KEY environment variable set")

    s3_bucket_name = os.environ.get("S3_CERT_BUCKET_NAME")
    if not s3_bucket_name:
        raise ValueError("S3_CERT_BUCKET_NAME environment variable set")

    s3_object_name = os.environ.get("S3_CERT_OBJECT_NAME")
    if not s3_object_name:
        raise ValueError("S3_CERT_OBJECT_NAME environment variable set")

    return gandi_token, notify_api_key, s3_bucket_name, s3_object_name


def main(testrun: bool = False, test_email: str = ""):

    gandi_token, notify_api_key, s3_bucket_name, s3_object_name = get_environment_variables()
    logger.info("Instantiating services...")
    gandi_service = GandiService(gandi_token, cert_config["CERT_URL_EXTENSION"])
    notify_service = NotifyService(cert_config, notify_api_key, MINISTRY_OF_JUSTICE)
    s3_service = S3Service(s3_bucket_name, MINISTRY_OF_JUSTICE,)

    logger.info("Extracting email map from S3")
    email_mappings = s3_service.get_json_file(s3_object_name, s3_object_name)

    logger.info("Extracting certificate list from Gandi...")
    certificate_list = gandi_service.get_certificate_list()
    valid_certificate_list = gandi_service.get_certificates_in_valid_state(
        certificate_list, email_mappings)
    if expired_certificate_list := gandi_service.get_expired_certificates_from_valid_certificate_list(
            valid_certificate_list, email_mappings, cert_config["CERT_EXPIRY_THRESHOLDS"]
    ):
        
        print("Building parameters to send emails...")
        email_parameter_list = notify_service.build_email_parameter_list_crs(
            expired_certificate_list)

        if testrun:
            logger.info("Sending test email to {test_email}...")
            notify_service.send_test_email_from_parameters_crs(
                email_parameter_list, test_email)
            logger.info("Building main report...")
            report = notify_service.build_main_report_string_crs(
                email_parameter_list)
            logger.info("Sending test report to %s...", test_email)
            notify_service.send_report_email_crs(
                report, cert_config["CERT_REPORT_TEMPLATE_ID"], test_email)

        else:
            logger.info("Sending live emails...")
            notify_service.send_emails_from_parameters_crs(email_parameter_list)
            print("Building live report...")
            report = notify_service.build_main_report_string_crs(
                email_parameter_list)
            print("Sending live report to Operations Engineering...")
            notify_service.send_report_email_crs(
                report, cert_config["CERT_REPORT_TEMPLATE_ID"], cert_config["CERT_REPLY_EMAIL"])
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
