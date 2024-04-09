from unittest import TestCase
from unittest.mock import patch, MagicMock, Mock

from bin.identify_dormant_github_users import (get_audit_logs, identify_dormant_users, identify_dormant_github_users, setup_environment)
from services.github_service import GithubService
from services.auth0_service import Auth0Service
from config.constants import RESPONSE_OKAY

import requests


class TestIdentifyDormantGithubUsers(TestCase):

    def setUp(self) -> None:
        self.response = Mock()
        self.response.status_code = RESPONSE_OKAY
        self.response.json.return_value = {"access_token": "test_access_token"}
        requests.post = MagicMock(return_value=self.response)

    @patch("sys.argv", ["test_github_token", "test_client_secret", "test_client_id", "test_domain"])
    def test_setup_environment(self):
        self.assertEqual(setup_environment(), ("test_github_token", "test_client_secret", "test_client_id", "test_domain"))

    @patch.object(Auth0Service, "get_active_users")
    def test_get_audit_logs(self, mock_auth0_users):
        mock_auth0_users.return_value = [
            {
                "test_key": "test_value",
                "last_login": "2050-01-01T00:00:00.000Z",
                "user_id": "user1"
            },
            {
                "test_key": "test_value",
                "last_login": "2050-01-01T00:00:00.000Z",
                "user_id": "user2"
            }
        ]

        auth0_service = Auth0Service("test_client_secret", "test_client_id", "test_domain", "test_grant_type")

        self.assertEqual(get_audit_logs(auth0_service), ["user1", "user2"])

    def test_identify_dormant_users(self):
        self.assertEqual(identify_dormant_users(["user1", "user2", "user3"], ["user1", "user2"]), ["user3"])

    @patch("gql.transport.aiohttp.AIOHTTPTransport.__new__", new=MagicMock)
    @patch("gql.Client.__new__", new=MagicMock)
    @patch("github.Github.__new__")
    @patch("bin.identify_dormant_github_users.setup_environment")
    @patch("bin.identify_dormant_github_users.get_audit_logs")
    @patch.object(GithubService, "get_users_of_multiple_organisations")
    @patch("bin.identify_dormant_github_users.identify_dormant_users")
    def test_identify_dormant_github_users(
        self,
        mock_identify_dormant_users,
        mock_get_users_if_multiple_organisations,
        mock_get_audit_logs,
        mock_setup_environment,
        _mock_github_client_core_api
    ):
        mock_setup_environment.return_value = ("test_github_token", "test_client_secret", "test_client_id", "test_domain")
        mock_get_audit_logs.return_value = ["user1", "user2", "user3"]
        mock_get_users_if_multiple_organisations.return_value = ["user1", "user2", "user3", "user4"]
        mock_identify_dormant_users.return_value = ["user4"]

        identify_dormant_github_users()

        mock_setup_environment.assert_called_once()
        mock_get_audit_logs.assert_called_once()
        mock_get_users_if_multiple_organisations.assert_called_once_with(["ministryofjustice", "moj-analytical-services"])
        mock_identify_dormant_users.assert_called_once_with(["user1", "user2", "user3", "user4"], ["user1", "user2", "user3"])
