import unittest
from unittest.mock import patch
from test.test_utils.test_config_certificates import test_config
from bin.report_certificate_expiry_undeliverable import main, get_environment_variables
from services.notify_service import NotifyService



@patch.dict('os.environ', {"NOTIFY_PROD_API_KEY": "test_notify_api_key"})
@patch.dict('bin.report_certificate_expiry_undeliverable.cert_config', test_config)
class TestUndeliverableReport(unittest.TestCase):

    def test_environment_variable_set(self):
        result = get_environment_variables()
        self.assertEqual(result, 'test_notify_api_key')

    @patch.dict('os.environ', {}, clear=True)
    def test_environment_variable_not_set(self):

        with self.assertRaises(ValueError) as context:
            get_environment_variables()
        self.assertIn("No NOTIFY_PROD_API_KEY environment variable set", str(context.exception))

    @patch.object(NotifyService, "__init__", return_value=None)
    @patch.object(NotifyService, "check_for_undelivered_emails_for_template")
    @patch.object(NotifyService, "build_undeliverable_email_report_string_crs")
    @patch.object(NotifyService, "send_report_email_crs")
    def test_main_run(self, mock_send_report, mock_build_report, mock_check_emails, mock_notify_init):
        mock_check_emails.return_value = ["undelivered_email1", "undelivered_email1"]
        mock_build_report.return_value = "Undelivered email report content"

        main(testrun=False)

        mock_notify_init.assert_called_once()
        mock_check_emails.assert_called_once_with("test_expiry_template_id")
        mock_build_report.assert_called_once_with(["undelivered_email1", "undelivered_email1"])
        mock_send_report.assert_called_once_with(
            "Undelivered email report content",
            "test_undelivered_report_template_id",
            "test_reply_email")

    @patch.object(NotifyService, "__init__", return_value=None)
    @patch.object(NotifyService, "check_for_undelivered_emails_for_template")
    @patch.object(NotifyService, "build_undeliverable_email_report_string_crs")
    @patch.object(NotifyService, "send_report_email_crs")
    def test_main_testrun(self, mock_send_report, mock_build_report, mock_check_emails, mock_notify_init):
        mock_check_emails.return_value = ["email1", "email2"]
        mock_build_report.return_value = "Test report content"

        main(testrun=True, test_email="testemail@gov.uk")

        mock_notify_init.assert_called_once()
        mock_check_emails.assert_called_once_with("test_expiry_template_id")
        mock_build_report.assert_called_once_with(["email1", "email2"])
        mock_send_report.assert_called_once_with(
            "Test report content",
            "test_undelivered_report_template_id",
            "testemail@gov.uk"
        )

    @patch.object(NotifyService, "__init__", return_value=None)
    @patch.object(NotifyService, "check_for_undelivered_emails_for_template", return_value=[])
    @patch.object(NotifyService, "build_undeliverable_email_report_string_crs")
    @patch.object(NotifyService, "send_report_email_crs")
    def test_no_undelivered_emails(self, mock_send_report, mock_build_report, mock_check_emails, mock_notify_init):

        main(testrun=True,  test_email="testemail@gov.uk")

        mock_notify_init.assert_called_once()
        mock_check_emails.assert_called_once_with("test_expiry_template_id")
        mock_build_report.assert_not_called()
        mock_send_report.assert_not_called()


if __name__ == "__main__":
    unittest.main()
