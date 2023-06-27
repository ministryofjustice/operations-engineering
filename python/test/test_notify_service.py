import unittest
from datetime import datetime, timezone
from unittest.mock import patch
import requests
from python.services.notify_service import NotifyService
from python.tests.test_config import test_config


class TestCheckForUndeliveredEmailsFromNotify(unittest.TestCase):

    def setUp(self):
        self.config = test_config
        self.api_key = "test_api_key"
        self.notify_service = NotifyService(self.config, self.api_key)
        self.template_id = "test_template_id"

    @patch.object(NotifyService, "_get_notifications_by_type_and_status")
    def test_undelivered_emails_not_found_returns_none(self, mock_get_notifications_by_type_and_status):
        mock_get_notifications_by_type_and_status.return_value = {
            "notifications": []
        }

        result = self.notify_service.check_for_undelivered_emails_for_template(
            self.template_id)
        self.assertEqual(len(result), 0)

    @patch.object(NotifyService, "_get_notifications_by_type_and_status")
    def test_undelivered_emails_found_returns_expected_data(self, mock_get_notifications_by_type_and_status):
        today = datetime.now(timezone.utc).date()
        mock_get_notifications_by_type_and_status.return_value = {
            "notifications": [
                {
                    "template": {"id": self.template_id},
                    "email_address": "test@example.com",
                    "created_at": today.isoformat(),
                    "status": "failed"
                }
            ]
        }

        result = self.notify_service.check_for_undelivered_emails_for_template(
            self.template_id)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["email_address"], "test@example.com")
        self.assertEqual(result[0]["created_at"], today)
        self.assertEqual(result[0]["status"], "failed")


@patch("python.services.notify_service.NotificationsAPIClient")
class TestSendEmailReplyToOpsEng(unittest.TestCase):

    def setUp(self):
        self.config = test_config
        self.api_key = "test_api_key"
        self.template_id = "test_template_id"
        self.ops_email = "test_ops_email"
        self.data_to_send = {"some-data": "the_data"}
        self.email_reply_to_id = '6767e190-996f-462c-b7f8-9bafe7b96a01'
        self.notify_service = NotifyService(self.config, self.api_key)

    def test_send_email_reply_to_ops_eng(self, mock_notifications_api_client):
        mock_notifications_api_client.return_value.send_email_notification.return_value = None
        self.notify_service.send_email_reply_to_ops_eng(
            self.template_id, self.ops_email, self.data_to_send)
        mock_notifications_api_client.return_value.send_email_notification.assert_called_once_with(
            email_address=self.ops_email,
            template_id=self.template_id,
            personalisation=self.data_to_send,
            email_reply_to_id=self.email_reply_to_id
        )

    def test_send_email_reply_to_ops_eng_raises_exception(self, mock_notifications_api_client):
        mock_notifications_api_client.return_value.send_email_notification.side_effect = requests.exceptions.HTTPError
        with self.assertRaises(requests.exceptions.HTTPError):
            self.notify_service.send_email_reply_to_ops_eng(
                self.template_id, self.ops_email, self.data_to_send)

# pylint: disable=W0212
@patch("python.services.notify_service.NotificationsAPIClient")
class TestGetNotificationsByTypeAndStatus(unittest.TestCase):

    def setUp(self):
        self.config = test_config
        self.api_key = "test_api_key"
        self.notify_service = NotifyService(self.config, self.api_key)

    def test_get_notifications_by_type_and_status(self, mock_notifications_api_client):
        mock_notifications_api_client.return_value.get_all_notifications.return_value = [
            "notification1", "notification2"]
        result = self.notify_service._get_notifications_by_type_and_status(
            'email', 'failed')
        self.assertEqual(result, ["notification1", "notification2"])


if __name__ == "__main__":
    unittest.main()
