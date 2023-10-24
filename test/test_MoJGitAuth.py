import unittest
from unittest.mock import patch
from lib.moj_git_auth import MoJGitAuth


class TestMoJGitAuth(unittest.TestCase):

    @patch('requests.post')
    def test_generate_installation_token_success(self, mock_post):
        mock_post.return_value.status_code = 201
        mock_post.return_value.json.return_value = {
            "token": "installation_token"}

        jwt_token = "sample_jwt_token"
        installation_id = "sample_installation_id"

        expected_result = mock_post.return_value.json()['token']

        self.assertEqual(expected_result, MoJGitAuth.generate_installation_token(
            installation_id, jwt_token))

    @patch('requests.post')
    def test_generate_installation_token_failed(self, mock_post):
        mock_post.return_value.status_code = 400

        jwt_token = "sample_jwt_token"
        installation_id = "sample_installation_id"

        expected_result = None

        self.assertEqual(expected_result, MoJGitAuth.generate_installation_token(
            installation_id, jwt_token))

    @patch('requests.get')
    def test_get_app_install_id_success(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = [{"id": "install_id"}]

        jwt_token = "sample_jwt_token"

        expected_result = mock_get.return_value.json()[0]["id"]

        self.assertEqual(
            expected_result, MoJGitAuth.get_app_install_id(jwt_token))

    @patch('requests.get')
    def test_get_app_install_id_failed(self, mock_get):
        mock_get.return_value.status_code = 401

        jwt_token = "sample_jwt_token"

        expected_result = None

        self.assertEqual(
            expected_result, MoJGitAuth.get_app_install_id(jwt_token))


if __name__ == '__main__':
    unittest.main()
