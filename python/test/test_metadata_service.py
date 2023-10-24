import unittest
from unittest.mock import MagicMock, patch
from python.services.metadata_service import MetadataService


class TestMetaDataService(unittest.TestCase):

    def setUp(self):
        self.api_url = "http://api.example.com"
        self.api_token = "xxx"
        self.metadata_service = MetadataService(
            api_url=self.api_url, api_token=self.api_token)

    def test_combine_user_data(self):
        slack_users = [
            {"username": "slack_user1", "email": "user1@example.com"},
            {"username": "slack_user2", "email": "user2@nomatch.com"}
        ]
        github_users = [
            {"username": "github_user1", "email": "user1@example.com"},
            {"username": "github_user2", "email": "user2@example.com"}
        ]

        expected_combined = [
            {"slack_username": "slack_user1",
                "github_username": "github_user1", "email": "user1@example.com"}
        ]

        result = self.metadata_service.combine_user_data(
            slack_users, github_users)
        self.assertEqual(result, expected_combined)


@patch('requests.post')
class TestMetadataService(unittest.TestCase):

    def setUp(self):
        self.api_url = "http://api.example.com"
        self.api_token = "xxx"
        self.metadata_service = MetadataService(
            api_url=self.api_url, api_token=self.api_token)

    def test_add_new_usernames_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_post.return_value = mock_response

        usernames_to_add = [
            {
                "slack_username": "slack_user1",
                "github_username": "github_user1",
                "email": "user1@example.com"
            },
            {
                "slack_username": "slack_user2",
                "github_username": "github_user2",
                "email": "user2@example.com"
            }
        ]

        self.metadata_service.add_new_usernames(usernames_to_add)

        mock_post.assert_called_once_with(
            f"{self.api_url}/user/add",
            json={"users": usernames_to_add},
        )

    def test_add_new_usernames_api_error(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.content = "Mock error message"
        mock_post.return_value = mock_response

        usernames_to_add = [
            {
                "slack_username": "slack_user1",
                "github_username": "github_user1",
                "email": "user1@example.com"
            },
            {
                "slack_username": "slack_user2",
                "github_username": "github_user2",
                "email": "user2@example.com"
            }
        ]

        with self.assertLogs(level='ERROR') as mock_error:
            self.metadata_service.add_new_usernames(usernames_to_add)

        self.assertEqual(mock_error.output, [
                         f"ERROR:root:Error adding new usernames: {mock_response.content}"])

    def test_add_new_usernames_exception(self, mock_post):
        mock_post.side_effect = Exception("API is down")

        usernames_to_add = [
            {
                "slack_username": "slack_user1",
                "github_username": "github_user1",
                "email": "user1@example.com"
            },
            {
                "slack_username": "slack_user2",
                "github_username": "github_user2",
                "email": "user2@example.com"
            }
        ]

        with self.assertLogs(level='ERROR') as mock_exception:
            self.metadata_service.add_new_usernames(usernames_to_add)

        self.assertEqual(mock_exception.output, [
                         "ERROR:root:An error occurred while adding new usernames: API is down"])


class FilterUsernamesTest(unittest.TestCase):

    def setUp(self):
        self.api_url = "http://api.example.com"
        self.api_token = "xxx"
        self.metadata_service = MetadataService(self.api_url, self.api_token)

        self.all_usernames = [
            {'username': 'user1', 'email': 'user1@example.com'},
            {'username': 'user2', 'email': 'user2@example.com'},
            {'username': 'user3', 'email': 'user3@example.com'}
        ]
        self.accepted_usernames = [
            {'username': 'user1'},
            {'username': 'user3'}
        ]

    def test_filter_usernames(self):
        filtered_usernames = self.metadata_service.filter_usernames(
            self.all_usernames, self.accepted_usernames)

        self.assertEqual(filtered_usernames, [
            {'username': 'user1', 'email': 'user1@example.com'},
            {'username': 'user3', 'email': 'user3@example.com'}
        ])


if __name__ == "__main__":
    unittest.main()
