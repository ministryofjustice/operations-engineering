import os
import unittest
from unittest.mock import MagicMock, patch

from python.scripts import close_support_tickets


@patch("github.Github.__new__", new=MagicMock)
@patch("gql.Client.__new__", new=MagicMock)
@patch("gql.transport.aiohttp.AIOHTTPTransport.__new__", new=MagicMock)
class TestCloseSupportTicketsMain(unittest.TestCase):

    @patch.dict(os.environ, {"ADMIN_GITHUB_TOKEN": "token"})
    def test_main_smoke_test(self):
        close_support_tickets.main()


@patch("github.Github.__new__", new=MagicMock)
@patch("gql.Client.__new__", new=MagicMock)
@patch("gql.transport.aiohttp.AIOHTTPTransport.__new__", new=MagicMock)
class TestCloseSupportTickets(unittest.TestCase):
    def test_raises_error_when_no_environment_variables_provided(self):
        self.assertRaises(
            ValueError, close_support_tickets.get_environment_variables)


if __name__ == "__main__":
    unittest.main()
