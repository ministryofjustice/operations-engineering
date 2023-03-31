import unittest
from unittest.mock import patch, MagicMock

from python.scripts import move_dependabot_tickets
from python.services.zenhub_service import ZenhubService


@patch("gql.Client.__new__", new=MagicMock)
@patch("gql.transport.aiohttp.AIOHTTPTransport.__new__", new=MagicMock)
class TestMoveDependabotTickets(unittest.TestCase):

    @patch("sys.argv", ["", "--api_token", "test"])
    @patch("gql.Client.__new__")
    def test_main(self, mock_gql_client):
        mock_gql_client.return_value = MagicMock()
        move_dependabot_tickets.main()

    def test_invalid_args(self):
        with self.assertRaises(SystemExit) as cm:
            move_dependabot_tickets.main()

        self.assertEqual(cm.exception.code, 2)

    def test_get_issues(self):
        svc = ZenhubService("123")
        svc.search_issues_by_label = MagicMock(return_value="test_issue_id")
        svc.get_pipeline_id = MagicMock(return_value="test_pipeline_id")

        self.assertEqual("test_issue_id", move_dependabot_tickets.get_issues(
            svc, "test_repo_id", "test_label"))

    def test_get_issues_returns_none_when_no_issues_found(self):
        svc = ZenhubService("123")
        svc.search_issues_by_label = MagicMock(return_value=None)
        svc.get_pipeline_id = MagicMock(return_value="test_pipeline_id")

        self.assertEqual(None, move_dependabot_tickets.get_issues(
            svc, "test_repo_id", "test_label"))

    def test_get_issues_returns_none_when_no_pipeline_found(self):
        svc = ZenhubService("123")
        svc.get_pipeline_id = MagicMock(return_value=None)

        with self.assertRaises(ValueError):
            move_dependabot_tickets.get_issues(
                svc, "test_repo_id", "test_label")

    def test_move_issues(self):
        svc = ZenhubService("123")
        svc.get_pipeline_id = MagicMock(return_value="test_pipeline_id")
        issues = [{"id": "test_issue_id"}]
        svc.zenhub_client_gql_api.execute.return_value = {
            "moveIssue": {
                "issue": {
                    "id": "issue_id",
                    "pipelineIssue": {
                        "pipeline": {
                            "id": "test_pipeline_id"
                        }
                    }
                }
            }
        }
        self.assertEqual(None, move_dependabot_tickets.move_issues(
            svc, issues, "test_pipeline_id"))

    def test_move_issues_without_pipeline_id(self):
        svc = ZenhubService("123")
        svc.get_pipeline_id = MagicMock(return_value=None)
        issues = [{"id": "test_issue_id"}]
        with self.assertRaises(ValueError):
            move_dependabot_tickets.move_issues(
                svc, issues, "test_pipeline_id")

    def test_move_issues_without_issue_id(self):
        svc = ZenhubService("123")
        svc.get_pipeline_id = MagicMock(return_value="test_pipeline_id")
        issues = [{"id": None}]
        svc.zenhub_client_gql_api.execute.return_value = {
            "moveIssue": {
                "issue": {
                    "id": "issue_id",
                    "pipelineIssue": {
                        "pipeline": {
                            "id": "test_pipeline_id"
                        }
                    }
                }
            }
        }

        self.assertEqual(None, move_dependabot_tickets.move_issues(
            svc, issues, "test_pipeline_id"))


if __name__ == '__main__':
    unittest.main()
