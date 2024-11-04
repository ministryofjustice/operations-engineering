import unittest
from datetime import datetime, timezone
from unittest.mock import patch
from test.files.test_config import test_config
import requests
from services.notify_service import NotifyService
from config.constants import MINISTRY_OF_JUSTICE, MOJ_ANALYTICAL_SERVICES

# pylint: disable=W0212, W0221


class TestCheckForUndeliveredEmailsFromNotify(unittest.TestCase):

    @patch("services.notify_service.NotificationsAPIClient")
    def setUp(self, mock_notify_client):
        self.config = test_config
        self.api_key = "test_api_key"
        self.notify_service = NotifyService(
            self.config, self.api_key, "some-org")
        self.notify_service.client = mock_notify_client
        self.template_id = "test_template_id"
        self.email_address = "test@example.com"

    @patch.object(NotifyService, "_get_notifications_by_type_and_status")
    def test_undelivered_emails_not_found_returns_none(self, mock_get_notifications_by_type_and_status):
        mock_get_notifications_by_type_and_status.return_value = {
            "notifications": []
        }

        result = self.notify_service._check_for_undelivered_emails_for_template(
            self.template_id)
        self.assertEqual(len(result), 0)

    @patch.object(NotifyService, "_get_notifications_by_type_and_status")
    def test_undelivered_emails_found_returns_expected_data(self, mock_get_notifications_by_type_and_status):
        today = datetime.now(timezone.utc).date()
        mock_get_notifications_by_type_and_status.return_value = {
            "notifications": [
                {
                    "template": {"id": self.template_id},
                    "email_address": self.email_address,
                    "created_at": today.isoformat(),
                    "status": "failed"
                }
            ]
        }

        result = self.notify_service._check_for_undelivered_emails_for_template(
            self.template_id)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["email_address"], self.email_address)
        self.assertEqual(result[0]["created_at"], today)
        self.assertEqual(result[0]["status"], "failed")


class TestSendEmailReplyToOpsEng(unittest.TestCase):

    @patch("services.notify_service.NotificationsAPIClient")
    def setUp(self, mock_notifications_api_client):
        self.config = test_config
        self.api_key = "test_api_key"
        self.template_id = "test_template_id"
        self.ops_email = "test_ops_email"
        self.data_to_send = {"some-data": "the_data"}
        self.email_reply_to_id = '6767e190-996f-462c-b7f8-9bafe7b96a01'
        self.notify_service = NotifyService(
            self.config, self.api_key, "some-org")
        self.notify_service.client = mock_notifications_api_client

    def test_send_email_reply_to_ops_eng(self):
        self.notify_service.client.send_email_notification.return_value = None
        self.notify_service._send_email_reply_to_ops_eng(
            self.template_id, self.ops_email, self.data_to_send)
        self.notify_service.client.send_email_notification.assert_called_once_with(
            email_address=self.ops_email,
            template_id=self.template_id,
            personalisation=self.data_to_send,
            email_reply_to_id=self.email_reply_to_id
        )

    def test_send_email_reply_to_ops_eng_raises_exception(self):
        self.notify_service.client.send_email_notification.side_effect = requests.exceptions.HTTPError
        with self.assertRaises(requests.exceptions.HTTPError):
            self.notify_service._send_email_reply_to_ops_eng(
                self.template_id, self.ops_email, self.data_to_send)


class TestGetNotificationsByTypeAndStatus(unittest.TestCase):

    @patch("services.notify_service.NotificationsAPIClient")
    def setUp(self, mock_notifications_api_client):
        self.config = test_config
        self.api_key = "test_api_key"
        self.notify_service = NotifyService(
            self.config, self.api_key, "some-org")
        self.notify_service.client = mock_notifications_api_client

    def test_get_notifications_by_type_and_status(self):
        self.notify_service.client.get_all_notifications.return_value = [
            "notification1", "notification2"]
        result = self.notify_service._get_notifications_by_type_and_status(
            'email', 'failed')
        self.assertEqual(result, ["notification1", "notification2"])


class TestMissingOrgName(unittest.TestCase):
    @patch("services.notify_service.NotificationsAPIClient")
    def setUp(self, mock_notifications_api_client):
        self.config = test_config
        self.api_key = "test_api_key"
        self.notify_service = NotifyService(
            self.config, self.api_key, "")
        self.notify_service.client = mock_notifications_api_client

    def test_get_first_email_template_id_wrong_org_name(self):
        with self.assertRaises(ValueError):
            self.notify_service._get_first_email_template_id()


class TestNotifyServiceFunctionsForAsOrg(unittest.TestCase):
    @patch("services.notify_service.NotificationsAPIClient")
    def setUp(self, mock_notifications_api_client):
        self.config = test_config
        self.api_key = "test_api_key"
        self.notify_service = NotifyService(
            self.config, self.api_key, MOJ_ANALYTICAL_SERVICES)
        self.notify_service.client = mock_notifications_api_client
        self.email_address = "test@example.com"

    @patch.object(NotifyService, "_send_email_reply_to_ops_eng")
    def test_send_first_email_as_org(self, mock_send_email_reply_to_ops_eng):
        self.notify_service.send_first_email(self.email_address, "today")
        mock_send_email_reply_to_ops_eng.assert_called_once_with(
            "ac0e8752-f550-4550-bff7-ba739a3f2977",
            self.email_address,
            {"login_date": "today"}
        )

    @patch.object(NotifyService, "_send_email_reply_to_ops_eng")
    def test_send_reminder_email_as_org(self, mock_send_email_reply_to_ops_eng):
        self.notify_service.send_reminder_email(self.email_address, "today")
        mock_send_email_reply_to_ops_eng.assert_called_once_with(
            "13863d96-7986-4c3b-967e-3123a6773896",
            self.email_address,
            {"login_date": "today"}
        )

    @patch.object(NotifyService, "_send_email_reply_to_ops_eng")
    def test_send_removed_email_as_org(self, mock_send_email_reply_to_ops_eng):
        self.notify_service.send_removed_email(self.email_address)
        mock_send_email_reply_to_ops_eng.assert_called_once_with(
            "762646ac-0f88-4371-8550-3b6acf66334a",
            self.email_address,
            {}
        )

    def test_get_first_email_template_id_as_org(self):
        self.assertEqual(self.notify_service._get_first_email_template_id(
        ), "ac0e8752-f550-4550-bff7-ba739a3f2977")


class TestNotifyServiceFunctionsForMojOrg(unittest.TestCase):
    @patch("services.notify_service.NotificationsAPIClient")
    def setUp(self, mock_notifications_api_client):
        self.config = test_config
        self.api_key = "test_api_key"
        self.notify_service = NotifyService(
            self.config, self.api_key, MINISTRY_OF_JUSTICE)
        self.notify_service.client = mock_notifications_api_client
        self.email_address = "test@example.com"

    @patch.object(NotifyService, "_send_email_reply_to_ops_eng")
    def test_send_first_email_moj_org(self, mock_send_email_reply_to_ops_eng):
        self.notify_service.send_first_email(self.email_address, "today")
        mock_send_email_reply_to_ops_eng.assert_called_once_with(
            "30351e8f-320b-4ebe-b0bf-d6aa0a7c607d",
            self.email_address,
            {"login_date": "today"}
        )

    @patch.object(NotifyService, "_send_email_reply_to_ops_eng")
    def test_send_reminder_email_moj_org(self, mock_send_email_reply_to_ops_eng):
        self.notify_service.send_reminder_email(self.email_address, "today")
        mock_send_email_reply_to_ops_eng.assert_called_once_with(
            "7405b6f8-9355-4572-8b8c-c73bc8cdee3c",
            self.email_address,
            {"login_date": "today"}
        )

    @patch.object(NotifyService, "_send_email_reply_to_ops_eng")
    def test_send_removed_email_moj_org(self, mock_send_email_reply_to_ops_eng):
        self.notify_service.send_removed_email(self.email_address)
        mock_send_email_reply_to_ops_eng.assert_called_once_with(
            "d1698bc9-7176-4d54-bece-e68d03d5896a",
            self.email_address,
            {}
        )

    def test_get_first_email_template_id_moj_org(self):
        self.assertEqual(self.notify_service._get_first_email_template_id(
        ), "30351e8f-320b-4ebe-b0bf-d6aa0a7c607d")

    @patch.object(NotifyService, "check_for_undelivered_emails_for_template")
    @patch.object(NotifyService, "_get_first_email_template_id")
    def test_check_for_undelivered_first_emails(self, mock_get_first_email_template_id, mock_check_for_undelivered_emails_for_template):
        mock_check_for_undelivered_emails_for_template.return_value = "some-value"
        self.assertEqual(
            self.notify_service.check_for_undelivered_first_emails(), "some-value")
        mock_get_first_email_template_id.assert_called_once()


if __name__ == "__main__":
    unittest.main()
