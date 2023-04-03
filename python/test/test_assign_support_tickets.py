import unittest
from unittest.mock import patch, MagicMock

import python.scripts.assign_support_tickets as assign_support_tickets


@patch("github.Github.__new__", new=MagicMock)
@patch("gql.Client.__new__", new=MagicMock)
@patch("gql.transport.aiohttp.AIOHTTPTransport.__new__", new=MagicMock)
class TestAssignSupportTicket(unittest.TestCase):

    @patch("sys.argv", [
        "",
        "--oauth-token",
        "fake",
        "--org",
        "fake",
        "--repo",
        "fake",
    ])
    def test_call_main_with_arguments(self):
        assign_support_tickets.main()

    @patch("sys.argv", ["", "--oauth-token"])
    def test_call_main_without_arguments(self):
        with self.assertRaises(SystemExit) as cm:
            assign_support_tickets.main()

        self.assertEqual(cm.exception.code, 2)

    @patch("sys.argv", ["", "--oauth-token", ""])
    def test_add_default_arguments(self):
        parser = assign_support_tickets.add_arguments()
        self.assertEqual(parser.org, "ministryofjustice")
        self.assertEqual(parser.repo, "operations-engineering")
        self.assertEqual(parser.tag, "Support")
        