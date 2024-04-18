import os
import unittest
from unittest.mock import MagicMock, patch

from bin.auth0_delete_inactive_users import (delete_inactive_users,
                                             get_auth0_client_details, main)


@patch.dict(os.environ, {"AUTH0_CLIENT_SECRET": "secret", "AUTH0_CLIENT_ID": "id", "AUTH0_DOMAIN": "domain"})
class TestAuth0DeleteInactiveUsers(unittest.TestCase):

    @patch("services.auth0_service.Auth0Service")
    def test_main_when_no_users(self, mock_auth0_service):
        mock_auth0_service.get_inactive_users.return_value = []
        delete_inactive_users(mock_auth0_service)
        mock_auth0_service.delete_user.assert_not_called()

    @patch("services.auth0_service.Auth0Service")
    def test_main_when_users(self, mock_auth0_service):
        mock_auth0_service.get_inactive_users.return_value = [
            {"user_id": "some-user"}]
        delete_inactive_users(mock_auth0_service)
        mock_auth0_service.delete_user.assert_called_once_with("some-user")

    @patch("bin.auth0_delete_inactive_users.Auth0Service", new=MagicMock)
    @patch("bin.auth0_delete_inactive_users.delete_inactive_users")
    def test_main(self, mock_delete_inactive_users):
        main()
        mock_delete_inactive_users.assert_called_once()


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
