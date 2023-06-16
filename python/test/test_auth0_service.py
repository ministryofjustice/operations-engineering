import unittest
from unittest.mock import MagicMock, Mock
import requests
from python.services.auth0_service import Auth0_Service


class test_Auth0Service(unittest.TestCase):
    def setUp(self) -> None:
        self.client_secret = "test_client_secret"
        self.client_id = "test_client_id"
        self.domain = "test_domain"
        self.grant_type = "test_grant_type"
        self.endpoint = "test_endpoint"

        response = Mock()
        response.status_code = 200
        response.json.return_value = {"access_token": "test_access_token"}
        requests.post = MagicMock(return_value=response)

        self.auth0 = Auth0_Service(
            client_secret=self.client_secret,
            client_id=self.client_id,
            domain=self.domain,
            grant_type=self.grant_type,
        )

    def test_constructor(self):
        self.assertEqual(self.auth0.client_secret, self.client_secret)
        self.assertEqual(self.auth0.client_id, self.client_id)
        self.assertEqual(self.auth0.domain, self.domain)
        self.assertEqual(self.auth0.grant_type, self.grant_type)

    def test_delete_user(self):

        mock_response = Mock()
        mock_response.status_code = 204

        self.auth0.delete = MagicMock(return_value=mock_response)

        # Call the delete_user method with the given user ID
        user_id = 'user123'
        response = self.auth0.delete_user(user_id)

        # Check that the delete method was called with the correct URL
        self.auth0.delete.assert_called_once_with('api/v2/users/user123')

        # Check that the delete_user method returns the mock response object
        self.assertEqual(response, mock_response.status_code)

        # Set up the mock response object again, this time with an error status code
        err_response = MagicMock(spec=requests.Response)
        err_response.status_code = 500

        # Set up the mock Auth0 client object
        self.auth0.delete = MagicMock(return_value=err_response)

        # Call the delete_user method with the same user ID again
        response = self.auth0.delete_user(user_id)

        # Check that the delete method was called with the correct URL
        self.auth0.delete.assert_called_with('api/v2/users/user123')

        # Check that the delete_user method returns the mock error response
        self.assertEqual(response, err_response.status_code)

    def test_get_access_token(self):
        response = Mock()
        response.status_code = 200
        response.json.return_value = {"access_token": "test_access_token"}
        requests.post = MagicMock(return_value=response)

        access_token = self.auth0.get_access_token()

        self.assertEqual(access_token, "test_access_token")

    def test_get_users(self):
        response = Mock()
        response.status_code = 200
        response.json.return_value = [{"test_key": "test_value"}]

        self.auth0.get = MagicMock(return_value=response)

        users = self.auth0.get_users()

        self.assertEqual(users, [{"test_key": "test_value"}])

    def test_get_inactive_users(self):

        datetime = MagicMock()

        # Pretend it is January 1st, 2022
        fake_date = datetime(2022, 1, 1)
        datetime.utcnow.return_value = fake_date

        response = Mock()
        response.status_code = 200
        response.json.return_value = [
            {"test_key": "test_value", "last_login": "2021-11-11T00:00:00.000Z",
                "user_id": "test_user_id1"},
        ]

        self.auth0.get = MagicMock(return_value=response)

        users = self.auth0.get_inactive_users()

        self.assertEqual(users, [{"test_key": "test_value",
                                 "last_login": "2021-11-11T00:00:00.000Z",
                                  "user_id":
                                  "test_user_id1"}])

    def test_get_active_users(self):

        datetime = MagicMock()

        # Pretend it is January 1st, 2022
        fake_date = datetime(2022, 1, 1)
        datetime.utcnow.return_value = fake_date

        response = Mock()
        response.status_code = 200
        response.json.return_value = [
            {"test_key": "test_value", "last_login": "2021-11-11T00:00:00.000Z",
                "user_id": "test_user_id1"},
        ]

        self.auth0.get = MagicMock(return_value=response)

        users = self.auth0.get_active_users()

        self.assertEqual(users, [])

    def test_get(self):
        response = Mock()
        response.status_code = 200

        self.auth0._make_request = MagicMock(return_value=response)

        res = self.auth0.get(self.endpoint)

        self.assertEqual(res.status_code, response.status_code)

    def test_delete(self):
        response = Mock()
        response.status_code = 200

        self.auth0._make_request = MagicMock(return_value=response)

        res = self.auth0.delete(self.endpoint)

        self.assertEqual(res.status_code, response.status_code)


if __name__ == "__main__":
    unittest.main()
