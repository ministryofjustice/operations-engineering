import unittest
from unittest.mock import patch, MagicMock
from python.scripts.auth0_delete_inactive_users import delete_inactive_users, main


class TestAuth0DeleteInactiveUsers(unittest.TestCase):

    @patch("python.services.auth0_service.Auth0Service")
    def test_main_when_no_users(self, mock_auth0_service):
        mock_auth0_service.get_inactive_users.return_value = []
        delete_inactive_users(mock_auth0_service)
        mock_auth0_service.delete_user.assert_not_called()

    @patch("python.services.auth0_service.Auth0Service")
    def test_main_when_users(self, mock_auth0_service):
        mock_auth0_service.get_inactive_users.return_value = [{"user_id":"some-user"}]
        delete_inactive_users(mock_auth0_service)
        mock_auth0_service.delete_user.assert_called_once_with("some-user")

    @patch("python.scripts.auth0_delete_inactive_users.Auth0Service", new=MagicMock)
    @patch("python.scripts.auth0_delete_inactive_users.delete_inactive_users")
    def test_main(self, mock_delete_inactive_users):
        main()
        mock_delete_inactive_users.assert_called_once()


if __name__ == "__main__":
    unittest.main()
