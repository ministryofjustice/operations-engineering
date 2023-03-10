import unittest
from unittest.mock import MagicMock, Mock, patch

from github import Github

import assign_support_tickets


@patch("github.Github.__new__", new=MagicMock)
class TestAssignSupportTicket(unittest.TestCase):

    @patch("sys.argv", ["", "test"])
    def test_valid_args_but_no_changes(self):
        with self.assertRaises(SystemExit) as cm:
            assign_support_tickets.main()

        self.assertEqual(cm.exception.code, 0)

    def test_invalid_args(self):
        with self.assertRaises(ValueError):
            assign_support_tickets.main()

    @patch("github.Github.get_repo", new=MagicMock)
    @patch("sys.argv", ["", "test"])
    def test_valid_args_with_changes(self):
        # Create a mock github call to a repository and return a list of issues
        mock_client = Mock(Github)
        mock_client.get_repo.return_value = mock_func(
            mock_client.get_repo("test"))
        mock_func.get_issues.return_value = [Mock()]


if __name__ == '__main__':
    unittest.main()
