import os
import unittest
from unittest.mock import MagicMock, patch

from python.scripts import close_support_tickets


@patch("github.Github.__new__", new=MagicMock)
class TestSentryProjectsRateLimiting(unittest.TestCase):

    @patch.dict(os.environ, {"ADMIN_GITHUB_TOKEN": "token"})
    def test_main_smoke_test(self):
        close_support_tickets.main()

    def test_main_returns_error_when_no_token_provided(self):
        self.assertRaises(
            ValueError, close_support_tickets.main)


if __name__ == "__main__":
    unittest.main()
