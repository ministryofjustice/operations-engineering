# pylint: disable=C0411
from datetime import datetime, timezone
import requests
from notifications_python_client.notifications import NotificationsAPIClient
from config.constants import MINISTRY_OF_JUSTICE, MOJ_ANALYTICAL_SERVICES


class NotifyService:
    def __init__(self, config, api_key, organisation_name: str):
        self.config = config
        self.client = NotificationsAPIClient(api_key)
        self.organisation_name = organisation_name.lower()

    def send_first_email(self, email_address: str, login_date: str):
        first_email_template_id = self._get_first_email_template_id()

        personalisation = {"login_date": login_date}
        self._send_email_reply_to_ops_eng(
            first_email_template_id,
            email_address,
            personalisation
        )

    def send_reminder_email(self, email_address: str, login_date: str):
        personalisation = {"login_date": login_date}

        template_id = ""
        if self.organisation_name == MINISTRY_OF_JUSTICE:
            template_id = "7405b6f8-9355-4572-8b8c-c73bc8cdee3c"

        if self.organisation_name == MOJ_ANALYTICAL_SERVICES:
            template_id = "13863d96-7986-4c3b-967e-3123a6773896"

        self._send_email_reply_to_ops_eng(
            template_id,
            email_address,
            personalisation
        )

    def _get_first_email_template_id(self) -> str | ValueError:
        template_id = ""
        if self.organisation_name == MINISTRY_OF_JUSTICE:
            template_id = "30351e8f-320b-4ebe-b0bf-d6aa0a7c607d"

        if self.organisation_name == MOJ_ANALYTICAL_SERVICES:
            template_id = "ac0e8752-f550-4550-bff7-ba739a3f2977"

        if template_id == "":
            raise ValueError("Notify template ID missing")
        return template_id

    def send_removed_email(self, email_address: str):
        removed_email_template_id = ""
        if self.organisation_name == MINISTRY_OF_JUSTICE:
            removed_email_template_id = "d1698bc9-7176-4d54-bece-e68d03d5896a"

        if self.organisation_name == MOJ_ANALYTICAL_SERVICES:
            removed_email_template_id = "762646ac-0f88-4371-8550-3b6acf66334a"

        personalisation = {}
        self._send_email_reply_to_ops_eng(
            removed_email_template_id,
            email_address,
            personalisation
        )

    def check_for_undelivered_first_emails(self):
        return self.check_for_undelivered_emails_for_template(
            self._get_first_email_template_id())

    def _get_notifications_by_type_and_status(self, template_type, status):
        return self.client.get_all_notifications(status=status, template_type=template_type)

    def check_for_undelivered_emails_for_template(self, template_id):
        notifications = self._get_notifications_by_type_and_status('email', 'failed')[
            'notifications']
        today = datetime.now(timezone.utc).date()

        undelivered_emails = []

        for notification in notifications:
            created_at = datetime.fromisoformat(
                notification['created_at']).date()

            if notification['template']['id'] == template_id and created_at == today:
                undelivered_email = {
                    "email_address": notification['email_address'],
                    "created_at": created_at,
                    "status": notification['status']
                }
                undelivered_emails.append(undelivered_email)
        return undelivered_emails

    def _send_email_reply_to_ops_eng(self, template_id: str, email: str, personalisation: dict):
        operations_engineering_email_id = "6767e190-996f-462c-b7f8-9bafe7b96a01"
        try:
            self.client.send_email_notification(
                email_address=email,
                template_id=template_id,
                personalisation=personalisation,
                email_reply_to_id=operations_engineering_email_id
            )
        except requests.exceptions.HTTPError as api_key_error:
            raise requests.exceptions.HTTPError(
                f"You may need to export your Notify API Key:\n {api_key_error}"
            ) from api_key_error

    def build_email_parameter_list_crs(self, valid_certificate_list):
        emails_parameter_list = []
        for valid_certificate in valid_certificate_list:
            params = {
                'email_addresses': valid_certificate_list.get(valid_certificate).get('emails'),
                'domain_name': valid_certificate,
                'csr_email': self.config['CERT_REPLY_EMAIL'],
                'end_date': valid_certificate_list.get(valid_certificate).get('expiry_date')
            }
            emails_parameter_list.append(params)
        return emails_parameter_list

    def _send_email_crs(self, email_params, recipients):
        for email in recipients:
            domain_name = self._remove_suffix_if_present(
                email_params['domain_name'])
            try:
                self.client.send_email_notification(
                    email_address=email,
                    template_id=self.config["CERT_EXPIRY_TEMPALATE_ID"],
                    personalisation={
                        "domain_name": domain_name,
                        "csr_email": email_params['csr_email'],
                        "end_date": email_params['end_date'].strftime('%d/%m/%Y')
                    }
                )
            except requests.exceptions.HTTPError as api_key_error:
                raise requests.exceptions.HTTPError(
                    f"You may need to export your Notify API Key:\n {api_key_error}"
                ) from api_key_error

    def send_emails_from_parameters_crs(self, email_parameter_list):
        for email_parameters in email_parameter_list:
            self._send_email_crs(email_parameters,
                                 email_parameters['email_addresses'])

    def send_test_email_from_parameters_crs(self, email_parameter_list, test_email):
        for email_parameters in email_parameter_list:
            self._send_email_crs(email_parameters, [test_email])

    def _remove_suffix_if_present(self, domain_name):
        base, sep, suffix = domain_name.rpartition('.')
        return base if sep == '.' and suffix.isdigit() else domain_name

    def build_main_report_string_crs(self, email_parameter_list):
        new_line = '\n'
        return "".join(
            f"Domain Name: {self._remove_suffix_if_present(email_parameter['domain_name'])}\n"
            f"Sent to:\n{''.join([f'{address}{new_line}' for address in email_parameter['email_addresses']])}"
            f"\nExpiry Date: {email_parameter['end_date']} \n\n"
            for email_parameter in email_parameter_list
        )

    def build_undeliverable_email_report_string_crs(self, undeliverable_email_list):
        return "".join(
            f"Email Address: {undeliverable_email['email_address']}\n"
            f"Sent at: {undeliverable_email['created_at']}\n"
            f"Status: {undeliverable_email['status']} \n\n"
            for undeliverable_email in undeliverable_email_list
        )

    def send_report_email_crs(self, report, template_id, email):
        try:
            self.client.send_email_notification(
                email_address=email,
                template_id=template_id,
                personalisation={
                    "report": report
                }
            )
        except requests.exceptions.HTTPError as api_key_error:
            raise requests.exceptions.HTTPError(
                f"You may need to export your Notify API Key:\n {api_key_error}"
            ) from api_key_error
