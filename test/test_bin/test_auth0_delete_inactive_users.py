import os
import unittest
from unittest.mock import Mock, patch

from bin.auth0_delete_inactive_users import get_auth0_client_details, main


class TestMain(unittest.TestCase):
    @patch('bin.auth0_delete_inactive_users.Auth0Service', return_value=Mock())
    @patch('bin.auth0_delete_inactive_users.get_auth0_client_details', return_value=('secret', 'id', 'domain'))
    def test_main(self, mock_get_auth0_client_details, mock_Auth0Service):
        main()
        mock_get_auth0_client_details.assert_called_once()
        mock_Auth0Service.assert_called_once_with(
            client_secret='secret',
            client_id='id',
            domain='domain',
            grant_type='client_credentials'
        )
        mock_Auth0Service.return_value.delete_inactive_users.assert_called_once()


class TestGetAuth0ClientDetails(unittest.TestCase):
    @patch.dict(os.environ, {"AUTH0_CLIENT_SECRET": "secret", "AUTH0_CLIENT_ID": "id", "AUTH0_DOMAIN": "domain"})
    def test_get_auth0_client_details_success(self):
        # Test that the function returns the correct values when the environment variables are set
        self.assertEqual(get_auth0_client_details(),
                         ("secret", "id", "domain"))

    @patch.dict(os.environ, {"AUTH0_CLIENT_SECRET": "", "AUTH0_CLIENT_ID": "", "AUTH0_DOMAIN": ""}, clear=True)
    def test_get_auth0_client_details_failure(self):
        # Test that the function raises a ValueError when the environment variables are not set
        with self.assertRaises(ValueError):
            get_auth0_client_details()


if __name__ == "__main__":
    unittest.main()
