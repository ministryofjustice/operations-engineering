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
        with self.assertRaises(SystemExit) as cm:
            assign_support_tickets.main()

        self.assertEqual(cm.exception.code, 2)

    def test_assign_issues_to_creator(self):
        issues = [
            MagicMock(
                labels=[
                    MagicMock(name="Support"),
                ],
                assignees=[],
                user=MagicMock(login="test"),
            ),
        ]
        assign_support_tickets.assign_issues_to_creator(issues)
        issues[0].edit.assert_called_once_with(assignees=["test"])

    def test_add_arguments(self):
        with self.assertRaises(SystemExit) as cm:
            assign_support_tickets.add_arguments()

        self.assertEqual(cm.exception.code, 2)

    @patch(assign_support_tickets.__name__ + ".identify_support_issues", return_value=[MagicMock()])
    def test_identify_support_issues(self):
        issues = [
            MagicMock(
                labels=[
                    MagicMock(name="Support"),
                ],
                assignees=[],
                user=MagicMock(login="test"),
            ),
        ]

        support = assign_support_tickets.identify_support_issues(
            issues, "Support"),
        print(support, issues)
        self.assertEqual(len(support), 1)


if __name__ == '__main__':
    unittest.main()
