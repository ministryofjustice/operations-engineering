import unittest
from unittest.mock import MagicMock, Mock, patch
import requests
from python.services.auth0_service import Auth0Service
from python.lib.utilities import get_past_date
from python.config.constants import (
    RESPONSE_OKAY,
    RESPONSE_NO_CONTENT
)


class TestAuth0Service(unittest.TestCase):
    def setUp(self) -> None:
        self.client_secret = "test_client_secret"
        self.client_id = "test_client_id"
        self.domain = "test_domain"
        self.grant_type = "test_grant_type"
        self.endpoint = "test_endpoint"
        self.datetime = MagicMock()

        # Pretend it is January 1st, 2022
        self.fake_date = self.datetime(2022, 1, 1)

        self.response = Mock()
        self.response.status_code = RESPONSE_OKAY
        self.response.json.return_value = {"access_token": "test_access_token"}
        requests.post = MagicMock(return_value=self.response)

        self.auth0 = Auth0Service(
            client_secret=self.client_secret,
            client_id=self.client_id,
            domain=self.domain,
            grant_type=self.grant_type,
        )

        self.users_with_id = [
            {
                "test_key": "test_value",
                "user_id": "test_user_id1"
            },
        ]

        self.users = [{"test_key": "test_value"}]

        self.active_users = [
            {
                "test_key": "test_value",
                "last_login": "2050-01-01T00:00:00.000Z",
                "user_id": "test_user_id1"
            },
        ]

        self.expired_users = [
            {
                "test_key": "test_value",
                "last_login": "2022-01-01T00:00:00.000Z",
                "user_id": "test_user_id1"
            },
        ]

    def test_constructor(self):
        self.assertEqual(self.auth0.client_secret, self.client_secret)
        self.assertEqual(self.auth0.client_id, self.client_id)
        self.assertEqual(self.auth0.domain, self.domain)
        self.assertEqual(self.auth0.grant_type, self.grant_type)

    def test_delete_user(self):
        self.response.status_code = RESPONSE_NO_CONTENT
        self.auth0.delete = MagicMock(return_value=self.response)

        # Call the delete_user method with the given user ID
        user_id = "user123"
        response = self.auth0.delete_user(user_id)

        # Check that the delete method was called with the correct URL
        self.auth0.delete.assert_called_once_with("api/v2/users/user123")

        # Check that the delete_user method returns the mock response object
        self.assertEqual(response, self.response.status_code)

        # Set up the mock response object again, this time with an error status code
        err_response = MagicMock(spec=requests.Response)
        err_response.status_code = 500

        # Set up the mock Auth0 client object
        self.auth0.delete = MagicMock(return_value=err_response)

        # Call the delete_user method with the same user ID again
        response = self.auth0.delete_user(user_id)

        # Check that the delete method was called with the correct URL
        self.auth0.delete.assert_called_with("api/v2/users/user123")

        # Check that the delete_user method returns the mock error response
        self.assertEqual(response, err_response.status_code)

    def test_get_access_token(self):
        requests.post = MagicMock(return_value=self.response)
        access_token = self.auth0.get_access_token()
        self.assertEqual(access_token, "test_access_token")

    def test_get_access_token_fails(self):
        self.response.status_code = RESPONSE_NO_CONTENT
        requests.post = MagicMock(return_value=self.response)
        self.assertRaises(Exception, self.auth0.get_access_token)

    def test_get_users(self):
        self.response.json.return_value = self.users
        self.auth0.get = MagicMock(return_value=self.response)
        users = self.auth0.get_users()
        self.assertEqual(users, self.users)

    def test_get_users_with_pages(self):
        large_list = self.users * 102
        small_list = self.users
        joint_list = small_list + large_list
        self.response.json.side_effect = [large_list, small_list]
        self.auth0.get = MagicMock(return_value=self.response)
        users = self.auth0.get_users(page=3)
        self.assertEqual(users, joint_list)

    def test_get_users_when_error(self):
        self.response.status_code = RESPONSE_NO_CONTENT
        self.auth0.get = MagicMock(return_value=self.response)
        users = self.auth0.get_users()
        self.assertEqual(users, [])

    def test_get_inactive_users_when_user_is_active(self):
        datetime = MagicMock()
        fake_date = get_past_date(3, 0, 0)
        datetime.utcnow.return_value = fake_date
        the_users = self.expired_users
        the_users[0].update(
            {"last_login": f"{fake_date:%Y-%m-%dT%H:%M:%S.%fZ}"})
        self.response.json.return_value = the_users
        self.auth0.get = MagicMock(return_value=self.response)
        users = self.auth0.get_inactive_users()
        self.assertEqual(users, [])

    def test_get_inactive_users(self):
        self.datetime.utcnow.return_value = self.fake_date
        self.response.json.return_value = self.expired_users
        self.auth0.get = MagicMock(return_value=self.response)
        users = self.auth0.get_inactive_users()
        self.assertEqual(users, self.expired_users)

    def test_get_inactive_users_when_user_never_logged_in(self):
        self.response.json.return_value = self.users_with_id
        self.auth0.get = MagicMock(return_value=self.response)
        users = self.auth0.get_inactive_users()
        self.assertEqual(users, self.users_with_id)

    def test_get_active_users_when_user_has_expired(self):
        self.datetime.utcnow.return_value = self.fake_date
        self.response.json.return_value = self.expired_users
        self.auth0.get = MagicMock(return_value=self.response)
        users = self.auth0.get_active_users()
        self.assertEqual(users, [])

    def test_get_active_users_when_user_never_logged_in(self):
        self.datetime.utcnow.return_value = self.fake_date
        self.response.json.return_value = self.users_with_id
        self.auth0.get = MagicMock(return_value=self.response)
        users = self.auth0.get_active_users()
        self.assertEqual(users, [])

    def test_get_active_users(self):
        datetime = MagicMock()
        fake_date = datetime(2050, 1, 1)
        datetime.utcnow.return_value = fake_date
        self.response.json.return_value = self.active_users
        self.auth0.get = MagicMock(return_value=self.response)
        users = self.auth0.get_active_users()
        self.assertEqual(users, self.active_users)

    # pylint: disable=W0212
    @patch.object(requests, 'request')
    def test_make_request(self, mock_requests):
        mock_requests.return_value = Mock(status_code=RESPONSE_OKAY)
        response = self.auth0._make_request("POST", "some-endpoint")
        self.assertEqual(RESPONSE_OKAY, response.status_code)

    # pylint: disable=W0212
    @patch.object(requests, 'request')
    def test_make_request_with_data(self, mock_requests):
        mock_requests.return_value = Mock(status_code=RESPONSE_OKAY)
        response = self.auth0._make_request(
            "POST", self.endpoint, "the-data")
        self.assertEqual(RESPONSE_OKAY, response.status_code)

    # pylint: disable=W0212
    def test_get(self):
        self.auth0._make_request = MagicMock(return_value=self.response)
        res = self.auth0.get(self.endpoint)
        self.assertEqual(res.status_code, self.response.status_code)

    # pylint: disable=W0212
    def test_delete(self):
        self.auth0._make_request = MagicMock(return_value=self.response)
        res = self.auth0.delete(self.endpoint)
        self.assertEqual(res.status_code, self.response.status_code)


if __name__ == "__main__":
    unittest.main()
