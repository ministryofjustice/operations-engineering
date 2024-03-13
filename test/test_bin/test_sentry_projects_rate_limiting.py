import unittest
from unittest.mock import patch
import json
import requests
from bin import sentry_projects_rate_limiting

SENTRY_URL = "https://sentry.io/api/0"


class TestSentry(unittest.TestCase):
    @patch("bin.sentry_projects_rate_limiting.get_sentry_token")
    @patch("bin.sentry_projects_rate_limiting.get_org_teams")
    @patch("bin.sentry_projects_rate_limiting.check_sentry_projects")
    def test_call_main(self, mock_check_sentry_projects, mock_get_org_teams, mock_get_sentry_token):
        sentry_projects_rate_limiting.main()
        mock_get_sentry_token.assert_called()
        mock_get_org_teams.assert_called()
        mock_check_sentry_projects.assert_called()

    @patch("bin.sentry_projects_rate_limiting.check_sentry_projects_teams")
    def test_check_sentry_projects_with_no_teams(self, mock_check_sentry_projects_teams):
        sentry_projects_rate_limiting.check_sentry_projects("", "", None)
        mock_check_sentry_projects_teams.assert_not_called()

    @patch("bin.sentry_projects_rate_limiting.get_project_keys")
    @patch("bin.sentry_projects_rate_limiting.print_project_key_info")
    def test_check_sentry_projects_with_teams_and_has_no_project_key(self, mock_print_project_key_info, mock_get_project_keys):
        teams = [{"name": "some-team", "projects": [{"slug": "some-slug",
                                                     "name": "some-name", "status": "some-status"}]}]
        mock_get_project_keys.return_value = None
        sentry_projects_rate_limiting.check_sentry_projects_teams("", "", teams)
        mock_get_project_keys.assert_called()
        mock_print_project_key_info.assert_not_called()

    @patch("bin.sentry_projects_rate_limiting.get_project_keys")
    @patch("bin.sentry_projects_rate_limiting.print_project_key_info")
    def test_check_sentry_projects_with_teams_and_has_project_key(self, mock_print_project_key_info, mock_get_project_keys):
        teams = [{"name": "some-team", "projects": [{"slug": "some-slug",
                                                     "name": "some-name", "status": "some-status"}]}]
        project_key = {"rateLimit": None}
        mock_get_project_keys.return_value = [project_key]
        sentry_projects_rate_limiting.check_sentry_projects_teams("", "", teams)
        mock_get_project_keys.assert_called()
        mock_print_project_key_info.assert_called()

    def test_print_project_key_info(self):
        project_key = {"name": "some-name",
                       "rateLimit": "some-rateLimit", "isActive": "some-vale"}
        sentry_projects_rate_limiting.print_project_key_info(project_key)
        project_key = {"name": "some-name",
                       "rateLimit": "some-rateLimit", "isActive": "some-vale"}
        sentry_projects_rate_limiting.print_project_key_info(project_key)
        project_key = {"name": "some-name",
                       "rateLimit": None, "isActive": None}
        sentry_projects_rate_limiting.print_project_key_info(project_key)

    @patch.dict('os.environ', {'SENTRY_TOKEN': 'test_token'})
    def test_get_sentry_token(self):
        token = sentry_projects_rate_limiting.get_sentry_token()
        self.assertEqual(token, 'test_token')

    def test_get_sentry_token_raises_exception(self):
        self.assertRaises(
            ValueError, sentry_projects_rate_limiting.get_sentry_token)

    @patch('requests.get')
    def test_get_org_teams(self, mock_get):
        headers = {}
        mock_response_json = '''{"name": "test_team", "projects": []}'''
        mock_get.return_value.status_code = 200
        mock_get.return_value.ok = True
        mock_get.return_value.content = mock_response_json
        mock_get.return_value.json.return_value = mock_response_json
        teams = sentry_projects_rate_limiting.get_org_teams(
            headers, SENTRY_URL)
        self.assertEqual(teams, json.loads(mock_response_json))

    @patch('requests.get')
    def test_get_org_teams_failed(self, mock_get):
        headers = {}
        mock_get.return_value.status_code = 404
        mock_get.return_value.ok = False
        mock_get.return_value.raise_for_status.side_effect = requests.exceptions.HTTPError()
        teams = sentry_projects_rate_limiting.get_org_teams(
            headers, SENTRY_URL)
        self.assertIsNone(teams)

    @patch('requests.get')
    def test_get_project_keys(self, mock_get):
        headers = {}
        project_slug = "test_project"
        mock_response_json = '''{"name": "test_project_key", "rateLimit": 10, "status": "active"}'''
        mock_get.return_value.status_code = 200
        mock_get.return_value.ok = True
        mock_get.return_value.content = mock_response_json
        mock_get.return_value.json.return_value = mock_response_json
        project_keys = sentry_projects_rate_limiting.get_project_keys(
            headers, SENTRY_URL, project_slug)
        self.assertEqual(project_keys, json.loads(mock_response_json))

    @patch('requests.get')
    def test_get_project_keys_failed(self, mock_get):
        headers = {}
        project_slug = "test_project"
        mock_get.return_value.status_code = 404
        mock_get.return_value.ok = False
        mock_get.return_value.raise_for_status.side_effect = requests.exceptions.HTTPError()
        project_keys = sentry_projects_rate_limiting.get_project_keys(
            headers, SENTRY_URL, project_slug)
        self.assertIsNone(project_keys)
