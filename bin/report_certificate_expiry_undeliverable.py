import os
import sys
import logging

from services.notify_service import NotifyService

from config.constants import MINISTRY_OF_JUSTICE

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


cert_config = {
    "CERT_REPLY_EMAIL": "certificates@digital.justice.gov.uk",
    "CERT_EXPIRY_TEMPALATE_ID": "06abd028-0a8f-43d9-a122-90a92f9b62ee",
    "CERT_UNDELIVERED_REPORT_TEMPALATE_ID": "6d0e7249-6b2d-4f0e-bf32-657e9300d09e"
}


def get_environment_variables():

    notify_api_key = os.environ.get("NOTIFY_PROD_API_KEY")
    if not notify_api_key:
        raise ValueError("No NOTIFY_PROD_API_KEY environment variable set")

    return notify_api_key


def main(testrun: bool = False, test_email: str = ""):

    notify_api_key = get_environment_variables()

    logger.info("Instantiating services...")
    notify_service = NotifyService(cert_config, notify_api_key, MINISTRY_OF_JUSTICE)

    print("Building undelivered email report...")
    if undelivered_email_report := notify_service.check_for_undelivered_emails_for_template(
        cert_config["CERT_EXPIRY_TEMPALATE_ID"]
    ):
        if testrun:
            logger.info("Building undelivered email report...")
            report = notify_service.build_undeliverable_email_report_string_crs(
                undelivered_email_report)
            logger.info("Sending test undelivered email test report to %s...", test_email)
            notify_service.send_report_email_crs(
                report, cert_config['CERT_UNDELIVERED_REPORT_TEMPALATE_ID'], test_email)
        else:
            logger.info("Building undelivered email live report...")
            report = notify_service.build_undeliverable_email_report_string_crs(
                    undelivered_email_report)
            logger.info("Sending live undelivered emailreport to Operations Engineering...")
            notify_service.send_report_email_crs(
                report, cert_config["CERT_UNDELIVERED_REPORT_TEMPALATE_ID"], cert_config["CERT_REPLY_EMAIL"])


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        if len(sys.argv) > 2:
            main(True, sys.argv[2])
        else:
            raise SystemExit('Email address of recipient expected.')
    else:
        main()
