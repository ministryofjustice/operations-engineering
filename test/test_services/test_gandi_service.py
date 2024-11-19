from unittest.mock import patch, MagicMock
import unittest
import requests
from freezegun import freeze_time
from services.gandi_service import GandiService
from test.test_utils.test_data_certificates import TestData
from test.test_utils.test_config_certificates import test_config


class TestGandiAccountBalance(unittest.TestCase):
    def setUp(self):
        self.token = "test_token"
        self.url_extension = "v5/organization/"
        self.org_id = "example_org_id"
        self.gandi_service = GandiService(self.token, self.url_extension)

    @patch("services.gandi_service.requests.get")
    def test_get_current_account_balance_from_org_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {"prepaid": {"amount": "100.00"}}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        balance = self.gandi_service.get_current_account_balance_from_org(self.org_id)
        self.assertEqual(balance, 100.00)
        mock_get.assert_called_once_with(
            url=f"https://api.gandi.net/v5/organization/{self.org_id}",
            headers={"Authorization": "Bearer test_token"},
            timeout=60
        )

    @patch("services.gandi_service.requests.get")
    def test_get_current_account_balance_from_org_http_error(self, mock_get):
        mock_get.side_effect = requests.exceptions.HTTPError("Unauthorized")

        with self.assertRaises(requests.exceptions.HTTPError):
            self.gandi_service.get_current_account_balance_from_org(self.org_id)

    @patch("services.gandi_service.requests.get")
    def test_get_current_account_balance_from_org_type_error(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        with self.assertRaises(KeyError):
            self.gandi_service.get_current_account_balance_from_org(self.org_id)


class TestGandiCertificateList(unittest.TestCase):
    def setUp(self):
        self.token = "test_token"
        self.url_extension = test_config["CERT_URL_EXTENSION"]
        self.org_id = "example_org_id"
        self.gandi_service = GandiService(self.token, self.url_extension)

    @patch("services.gandi_service.requests.get")
    def test_get_certificate_list(self, mock_get):
        expected_data = [{"id": 1, "name": "example.com"},
                         {"id": 2, "name": "example.net"}]
        mock_response = MagicMock()
        mock_response.json.return_value = expected_data
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        expected_result = expected_data
        actual_result = self.gandi_service.get_certificate_list()

        self.assertEqual(actual_result, expected_result)
        mock_get.assert_called_once_with(
            url=f"https://api.gandi.net/{self.url_extension}",
            params={"per_page": 1000},
            headers={"Authorization": "Bearer test_token"},
            timeout=60
        )

    @patch('services.gandi_service.requests.get')
    def test_throws_http_error(self, mock_get):
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            'Unauthorized')
        mock_get.return_value = mock_response

        with self.assertRaises(requests.exceptions.HTTPError) as context:
            self.gandi_service.get_certificate_list()

        expected_message = "You may need to export your Gandi API key:\n Unauthorized"
        self.assertEqual(str(context.exception), expected_message)
        mock_get.assert_called_once_with(
            url=f"https://api.gandi.net/{self.url_extension}",
            params={"per_page": 1000},
            headers={"Authorization": "Bearer test_token"},
            timeout=60
        )

    @patch('services.gandi_service.requests.get')
    def test_throws_type_error(self, mock_get):
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = TypeError(
            'Invalid API key')
        mock_get.return_value = mock_response

        with self.assertRaises(TypeError) as context:
            self.gandi_service.get_certificate_list()

        expected_message = "Gandi API key does not exist or is in the wrong format:\n Invalid API key"
        self.assertEqual(str(context.exception), expected_message)
        mock_get.assert_called_once_with(
            url=f"https://api.gandi.net/{self.url_extension}",
            params={'per_page': 1000},
            headers={"Authorization": "Bearer test_token"},
            timeout=60
        )


@freeze_time("2023-01-01")
class TestGetExpiredCertificates(unittest.TestCase):
    def setUp(self):
        self.token = "test_token"
        self.url_extension = test_config["CERT_URL_EXTENSION"]
        self.org_id = "example_org_id"
        self.gandi_service = GandiService(self.token, self.url_extension)

    def test_valid_certificate_list_returns_expected_domain(self):
        response = self.gandi_service.get_expired_certificates_from_valid_certificate_list(
            TestData.generate_single_filtered_certificate_list_with_expiry_date(
                30),
            TestData.generate_single_email_list(),
            test_config["CERT_EXPIRY_THRESHOLDS"])

        self.assertIn(TestData.test_domain_name_root, response)

    def test_valid_certificate_list_returns_multiple_expected_domains(self):
        test_case_count = 3
        response = self.gandi_service.get_expired_certificates_from_valid_certificate_list(
            TestData.generate_multiple_filtered_certificate_list_with_expiry_date(
                30, test_case_count),
            TestData.generate_multiple_email_list(test_case_count),
            test_config["CERT_EXPIRY_THRESHOLDS"])

        self.assertIn(f"{TestData.test_domain_name_root}0", response)
        self.assertIn(f"{TestData.test_domain_name_root}1", response)
        self.assertIn(f"{TestData.test_domain_name_root}2", response)

    def test_valid_certificate_list_returns_single_expected_email(self):
        response = self.gandi_service.get_expired_certificates_from_valid_certificate_list(
            TestData.generate_single_filtered_certificate_list_with_expiry_date(
                30),
            TestData.generate_single_email_list(),
            test_config["CERT_EXPIRY_THRESHOLDS"])

        self.assertIn(TestData.test_recipient_email_root,
                      response[TestData.test_domain_name_root]['emails'])

    def test_valid_certificate_list_returns_multiple_expected_emails(self):
        response = self.gandi_service.get_expired_certificates_from_valid_certificate_list(
            TestData.generate_single_filtered_certificate_list_with_expiry_date(
                30),
            TestData.generate_single_email_list(recipcc=3),
            test_config["CERT_EXPIRY_THRESHOLDS"])

        self.assertIn(TestData.test_recipient_email_root,
                      response[TestData.test_domain_name_root]['emails'])
        self.assertIn(f"{TestData.test_recipientcc_email_root}{0}",
                      response[TestData.test_domain_name_root]['emails'])
        self.assertIn(f"{TestData.test_recipientcc_email_root}{1}",
                      response[TestData.test_domain_name_root]['emails'])
        self.assertIn(f"{TestData.test_recipientcc_email_root}{2}",
                      response[TestData.test_domain_name_root]['emails'])

    def test_valid_certificate_list_returns_expected_cname(self):
        test_case_count = 3
        response = self.gandi_service.get_expired_certificates_from_valid_certificate_list(
            TestData.generate_single_filtered_certificate_list_with_expiry_date(
                30),
            TestData.generate_single_email_list(cname=test_case_count),
            test_config["CERT_EXPIRY_THRESHOLDS"])

        self.assertIn(f"{TestData.test_cname_email_root}{0}",
                      response[TestData.test_domain_name_root]['emails'])
        self.assertIn(f"{TestData.test_cname_email_root}{1}",
                      response[TestData.test_domain_name_root]['emails'])
        self.assertIn(f"{TestData.test_cname_email_root}{2}",
                      response[TestData.test_domain_name_root]['emails'])


@freeze_time("2023-01-01")
class TestCertificateRetrievalValidity(unittest.TestCase):
    def setUp(self):
        self.token = "test_token"
        self.url_extension = test_config["CERT_URL_EXTENSION"]
        self.org_id = "example_org_id"
        self.gandi_service = GandiService(self.token, self.url_extension)

    def test_only_valid_certificates_are_returned_from_list(self):
        response = self.gandi_service.get_certificates_in_valid_state(
            TestData.generate_single_gandi_certificate_state('valid'),
            TestData.generate_single_email_list()
        )
        self.assertIn(TestData.test_domain_name_root, response)

    def test_invalid_certificate_is_not_returned(self):
        response = self.gandi_service.get_certificates_in_valid_state(
            TestData.generate_single_gandi_certificate_state('pending'),
            TestData.generate_single_email_list()
        )
        self.assertNotIn(TestData.test_domain_name_root, response)

    def test_multiple_valid_certificates_returned(self):
        test_case_count = 3
        response = self.gandi_service.get_certificates_in_valid_state(
            TestData.generate_multiple_gandi_certificate_states(
                'valid', test_case_count),
            TestData.generate_multiple_email_list(test_case_count)
        )

        self.assertIn(f"{TestData.test_domain_name_root}0", response)
        self.assertIn(f"{TestData.test_domain_name_root}1", response)
        self.assertIn(f"{TestData.test_domain_name_root}2", response)

    def test_multiple_valid_certificates_returned_with_same_domain_name(self):
        test_case_count = 3
        response = self.gandi_service.get_certificates_in_valid_state(
            TestData.generate_multiple_gandi_certificate_states_same_domain_name(
                'valid', test_case_count),
            TestData.generate_single_email_list()
        )

        self.assertIn(f"{TestData.test_domain_name_root}", response)
        self.assertIn(f"{TestData.test_domain_name_root}.1", response)
        self.assertIn(f"{TestData.test_domain_name_root}.2", response)

    def test_only_valid_certificate_is_returned(self):
        test_case_count = 3
        test_cases = TestData.generate_multiple_gandi_certificate_states(
            'pending', test_case_count)
        test_cases += TestData.generate_single_gandi_certificate_state('valid')
        test_email_list = TestData.generate_multiple_email_list(
            test_case_count)
        test_email_list.update(TestData.generate_single_email_list())

        response = self.gandi_service.get_certificates_in_valid_state(
            test_cases,
            test_email_list
        )

        self.assertNotIn(f"{TestData.test_domain_name_root}0", response)
        self.assertNotIn(f"{TestData.test_domain_name_root}1", response)
        self.assertNotIn(f"{TestData.test_domain_name_root}2", response)
        self.assertIn(TestData.test_domain_name_root, response)


if __name__ == '__main__':
    unittest.main()
