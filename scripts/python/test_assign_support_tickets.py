import unittest
from unittest.mock import MagicMock, patch

import assign_support_tickets


@patch("github.Github.__new__", new=MagicMock)
class TestAssignSupportTicket(unittest.TestCase):

    @patch("sys.argv", [
                    "",
                    "--oauth_token",
                    "fake",
                    "--org",
                    "fake",
                    "--repo",
                    "fake",
               ])
    def test_valid_args_but_no_changes(self):
        with self.assertRaises(SystemExit) as cm:
            assign_support_tickets.main()

        self.assertEqual(cm.exception.code, 0)

    def test_invalid_args(self):
        with self.assertRaises(SystemExit):
            assign_support_tickets.main()


if __name__ == '__main__':
    unittest.main()
