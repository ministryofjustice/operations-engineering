import unittest
from unittest.mock import patch
import json
import requests
from python.scripts import sentry_projects_rate_limiting

SENTRY_URL = "https://sentry.io/api/0"

class TestSentry(unittest.TestCase):

    @patch.dict('os.environ', {'SENTRY_TOKEN': 'test_token'})
    def test_get_sentry_token(self):
        token = sentry_projects_rate_limiting.get_sentry_token()
        self.assertEqual(token, 'test_token')

    @patch('requests.get')
    def test_get_org_teams(self, mock_get):
        headers = {}
        mock_response_json = '''{"name": "test_team", "projects": []}'''
        mock_get.return_value.status_code = 200
        mock_get.return_value.ok = True
        mock_get.return_value.content = mock_response_json
        mock_get.return_value.json.return_value = mock_response_json
        teams = sentry_projects_rate_limiting.get_org_teams(headers, SENTRY_URL)
        self.assertEqual(teams, json.loads(mock_response_json))

    @patch('requests.get')
    def test_get_org_teams_failed(self, mock_get):
        headers = {}
        mock_get.return_value.status_code = 404
        mock_get.return_value.ok = False
        mock_get.return_value.raise_for_status.side_effect = requests.exceptions.HTTPError()
        teams = sentry_projects_rate_limiting.get_org_teams(headers, SENTRY_URL)
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
