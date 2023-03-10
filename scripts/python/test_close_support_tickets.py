import unittest
from unittest.mock import MagicMock, patch

import close_support_tickets


@patch("github.Github.__new__", new=MagicMock)
class TestSentryProjectsRateLimiting(unittest.TestCase):

    def test_main_smoke_test(self):
        close_support_tickets.main()

if __name__ == "__main__":
    unittest.main()
