from unittest.mock import patch, MagicMock
import unittest
import requests
from services.gandi_service import GandiService


class TestGandiService(unittest.TestCase):
    def setUp(self):
        self.token = "test_token"
        self.url_extension = "v5/organization/"
        self.org_id = "example_org_id"
        self.gandi_service = GandiService(self.token, self.org_id)

    @patch('services.gandi_service.requests.get')
    def test_get_current_account_balance_from_org_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {'prepaid': {'amount': '100.00'}}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        balance = self.gandi_service.get_current_account_balance_from_org()
        self.assertEqual(balance, 100.00)

    @patch('services.gandi_service.requests.get')
    def test_get_current_account_balance_from_org_http_error(self, mock_get):
        mock_get.side_effect = requests.exceptions.HTTPError("Unauthorized")

        with self.assertRaises(requests.exceptions.HTTPError):
            self.gandi_service.get_current_account_balance_from_org()

    @patch('services.gandi_service.requests.get')
    def test_get_current_account_balance_from_org_type_error(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        with self.assertRaises(KeyError):
            self.gandi_service.get_current_account_balance_from_org()


if __name__ == '__main__':
    unittest.main()
