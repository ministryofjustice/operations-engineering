import unittest
from unittest.mock import patch
from test.test_utils.test_config_certificates import test_config
from bin.check_certificate_expiry import main, get_environment_variables
from services.gandi_service import GandiService
from services.notify_service import NotifyService
from services.s3_service import S3Service
from config.constants import MINISTRY_OF_JUSTICE


@patch.dict('os.environ', {
    "GANDI_CERTIFICATES_TOKEN": "test_gandi_token",
    "NOTIFY_PROD_API_KEY": "test_notify_api_key",
    "S3_CERT_BUCKET_NAME": "test_bucket",
    "S3_CERT_OBJECT_NAME": "test_object"
})
@patch.dict('bin.check_certificate_expiry.cert_config', test_config)
class TestCertificateExpiryCheck(unittest.TestCase):

    def test_get_environment_variables(self):
        result = get_environment_variables()
        self.assertEqual(result, (
            "test_gandi_token",
            "test_notify_api_key",
            "test_bucket",
            "test_object"
        ))

    @patch.dict('os.environ', {}, clear=True)
    def test_environment_variables_not_set(self):
        with self.assertRaises(ValueError) as context:
            get_environment_variables()
        self.assertIn("No GANDI_CERTIFICATES_TOKEN environment variable set", str(context.exception))

    @patch.object(GandiService, "__init__", return_value=None)
    @patch.object(NotifyService, "__init__", return_value=None)
    @patch.object(S3Service, "__init__", return_value=None)
    @patch.object(GandiService, "get_certificate_list")
    @patch.object(GandiService, "get_certificates_in_valid_state")
    @patch.object(GandiService, "get_expired_certificates_from_valid_certificate_list")
    @patch.object(S3Service, "get_json_file")
    @patch.object(NotifyService, "build_email_parameter_list_crs")
    @patch.object(NotifyService, "send_test_email_from_parameters_crs")
    @patch.object(NotifyService, "build_main_report_string_crs")
    @patch.object(NotifyService, "send_report_email_crs")
    def test_main_testrun(self, mock_send_report, mock_build_report, mock_send_test_email,
                          mock_build_email_params, mock_get_json, mock_get_expired_certificates,
                          mock_get_valid_certificates, mock_get_certificate_list,
                          mock_s3_init, mock_notify_init, mock_gandi_init):

        mock_get_certificate_list.return_value = ["test_cert1", "test_cert2"]
        mock_get_valid_certificates.return_value = ["valid_test_cert1", "valid_test_cert2"]
        mock_get_expired_certificates.return_value = ["expired_test_cert"]
        mock_get_json.return_value = {"cert1@example.com": "cert_owner@example.com"}
        mock_build_email_params.return_value = [{"recipient": "test_recipient"}]
        mock_build_report.return_value = "Test report content"

        main(testrun=True, test_email="testemail@gov.uk")

        mock_gandi_init.assert_called_once_with("test_gandi_token", "v5/certificate/issued-certs")
        mock_notify_init.assert_called_once_with(test_config, "test_notify_api_key", MINISTRY_OF_JUSTICE)
        mock_s3_init.assert_called_once_with("test_bucket", MINISTRY_OF_JUSTICE)

        mock_get_certificate_list.assert_called_once()
        mock_get_valid_certificates.assert_called_once_with(["test_cert1", "test_cert2"], mock_get_json.return_value)
        mock_get_expired_certificates.assert_called_once_with(["valid_test_cert1", "valid_test_cert2"], mock_get_json.return_value,
                                                              test_config["CERT_EXPIRY_THRESHOLDS"])
        mock_build_email_params.assert_called_once_with(["expired_test_cert"])
        mock_send_test_email.assert_called_once_with([{"recipient": "test_recipient"}], "testemail@gov.uk")
        mock_send_report.assert_called_once_with("Test report content", 'test_report_template_id', "testemail@gov.uk")


if __name__ == "__main__":
    unittest.main()
