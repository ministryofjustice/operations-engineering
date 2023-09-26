import unittest
from unittest.mock import patch, MagicMock
from python.scripts import assign_support_tickets
from python.services.github_service import GithubService
from python.test.test_github_service import MockGithubIssue


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

    @patch("sys.argv", [
        "",
        "--oauth-token",
        "fake",
        "--org",
        "fake",
        "--repo",
        "fake",
    ])
    @patch.object(GithubService, "__new__")
    def test_call_main_catches_exception(self, github_service_mock):
        github_service_mock.return_value.assign_support_issues_to_self = MagicMock(
            side_effect=ValueError)
        with self.assertRaises(ValueError) as cm:
            assign_support_tickets.main()

    @patch("sys.argv", [
        "",
        "--oauth-token",
        "fake",
        "--org",
        "fake",
        "--repo",
        "fake",
    ])
    @patch.object(GithubService, "__new__")
    def test_call_main_no_issues(self, mock_github_service):
        mock_github_service.assign_support_issues_to_self.return_value = []
        assign_support_tickets.main()

    @patch("sys.argv", [
        "",
        "--oauth-token",
        "fake",
        "--org",
        "fake",
        "--repo",
        "fake",
    ])
    @patch.object(GithubService, "assign_support_issues_to_self")
    def test_call_main_with_issues(self, mock_assign_support_issues_to_self):
        the_object = MockGithubIssue(
            123, 456, "test complete", [], ["test_support_label"])
        mock_assign_support_issues_to_self.return_value = [the_object]
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


if __name__ == "__main__":
    unittest.main()
