from datetime import datetime, timezone
import requests
from notifications_python_client.notifications import NotificationsAPIClient
from python.config.logging_config import logging


class NotifyService:
    def __init__(self, config, api_key):
        self.config = config
        self.api_key = api_key
        self.operations_engineering_email_id = "6767e190-996f-462c-b7f8-9bafe7b96a01"

    def _get_notifications_by_type_and_status(self, template_type, status):
        return NotificationsAPIClient(self.api_key).get_all_notifications(status=status, template_type=template_type)

    def check_for_undelivered_emails_for_template(self, template_id):
        logging.debug("check_for_undelivered_emails_for_template")
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

    def send_email_reply_to_ops_eng(self, template_id: str, email: str, personalisation: dict):
        logging.debug("send_email_reply_to_ops_eng")
        try:
            NotificationsAPIClient(self.api_key).send_email_notification(
                email_address=email,
                template_id=template_id,
                personalisation=personalisation,
                email_reply_to_id=self.operations_engineering_email_id
            )
        except requests.exceptions.HTTPError as api_key_error:
            raise requests.exceptions.HTTPError(
                f"You may need to export your Notify API Key:\n {api_key_error}"
            ) from api_key_error
