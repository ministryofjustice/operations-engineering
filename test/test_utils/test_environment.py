import unittest
from unittest.mock import patch

from utils.environment import EnvironmentVariables


class TestEnvironmentVariables(unittest.TestCase):

    @patch.dict('os.environ', {'GH_ADMIN_TOKEN': 'fake_github_token', 'ADMIN_SLACK_TOKEN': 'fake_slack_token'})
    def test_all_env_vars_set(self):
        env_vars = EnvironmentVariables(
            ['GH_ADMIN_TOKEN', 'ADMIN_SLACK_TOKEN'])
        self.assertEqual(env_vars.get('GH_ADMIN_TOKEN'), 'fake_github_token')
        self.assertEqual(env_vars.get('ADMIN_SLACK_TOKEN'), 'fake_slack_token')

    @patch.dict('os.environ', {})
    def test_missing_env_vars(self):
        with self.assertRaises(EnvironmentError):
            EnvironmentVariables(['GH_ADMIN_TOKEN', 'ADMIN_SLACK_TOKEN'])

    @patch.dict('os.environ', {'GH_ADMIN_TOKEN': 'fake_github_token'})
    def test_partial_env_vars_set(self):
        with self.assertRaises(EnvironmentError):
            EnvironmentVariables(['GH_ADMIN_TOKEN', 'ADMIN_SLACK_TOKEN'])

    @patch.dict('os.environ', {'GH_ADMIN_TOKEN': 'fake_github_token', 'ADMIN_SLACK_TOKEN': 'fake_slack_token'})
    def test_extra_env_vars(self):
        env_vars = EnvironmentVariables(
            ['GH_ADMIN_TOKEN', 'ADMIN_SLACK_TOKEN', 'EXTRA_VAR'])
        self.assertEqual(env_vars.get('GH_ADMIN_TOKEN'), 'fake_github_token')
        self.assertEqual(env_vars.get('ADMIN_SLACK_TOKEN'), 'fake_slack_token')
        self.assertIsNone(env_vars.get('EXTRA_VAR'))


if __name__ == '__main__':
    unittest.main()
