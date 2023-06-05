import os
import unittest
from unittest.mock import MagicMock, patch

from python.scripts import sentry_usage_alert


@patch("requests.get", new=MagicMock)
class TestSentryUsageAlertMain(unittest.TestCase):

    @patch.dict(os.environ, {"SENTRY_TOKEN": "token"})
    def test_main_smoke_test(self):
        sentry_usage_alert.main()


@patch("requests.get", new=MagicMock)
class TestAddUsersEveryoneGithubTeamGetEnvironmentVariables(unittest.TestCase):
    def test_raises_error_when_no_environment_variables_provided(self):
        self.assertRaises(
            ValueError, sentry_usage_alert.get_environment_variables)

    @patch.dict(os.environ, {"SENTRY_TOKEN": "token"})
    def test_returns_values(self):
        sentry_token = sentry_usage_alert.get_environment_variables()
        self.assertEqual(sentry_token, "token")


if __name__ == "__main__":
    unittest.main()
