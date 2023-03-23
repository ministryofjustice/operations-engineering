import os
import unittest
from unittest.mock import MagicMock, patch

from python.scripts import sentry_projects_rate_limiting


@patch("requests.get", new=MagicMock(status_code=200))
class TestSentryProjectsRateLimiting(unittest.TestCase):

    @patch.dict(os.environ, {"SENTRY_TOKEN": "token"})
    def test_main_smoke_test(self):
        sentry_projects_rate_limiting.main()

    def test_main_returns_error_when_no_token_provided(self):
        self.assertRaises(
            ValueError, sentry_projects_rate_limiting.main)


if __name__ == "__main__":
    unittest.main()
