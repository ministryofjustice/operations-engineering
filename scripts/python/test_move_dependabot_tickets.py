import unittest
from unittest.mock import patch, MagicMock

import move_dependabot_tickets
from services.ZenhubService import ZenhubService


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

    @patch("services.ZenhubService.ZenhubService.get_pipeline_id")
    @patch("services.ZenhubService.ZenhubService.search_issues_by_label")
    def test_get_issues(self, mock_search_issues_by_label, mock_get_pipeline_id):
        mock_search_issues_by_label.return_value = "test_issue_id"
        mock_get_pipeline_id.return_value = "test_pipeline_id"
        svc = ZenhubService("123")

        self.assertEqual("test_issue_id", move_dependabot_tickets.get_issues(svc, "test_repo_id", "test_label"))

    @patch("services.ZenhubService.ZenhubService.get_pipeline_id")
    @patch("gql.Client.__new__")
    def test_get_issues_returns_none_when_no_issues_found(self, mock_gql_client, mock_get_pipeline_id):
        mock_get_pipeline_id.return_value = "test_pipeline_id"
        mock_gql_client.return_value = MagicMock()
        svc = ZenhubService("123")
        svc.search_issues_by_label = MagicMock(return_value=None)

        self.assertEqual(None, move_dependabot_tickets.get_issues(svc, "test_repo_id", "test_label"))

    @patch("gql.Client.__new__")
    def test_get_issues_returns_none_when_no_pipeline_found(self, mock_gql_client):
        mock_gql_client.return_value = MagicMock()
        svc = ZenhubService("123")
        svc.get_pipeline_id = MagicMock(return_value=None)

        # expecting to get a ValueError when no pipeline is found
        with self.assertRaises(ValueError):
            move_dependabot_tickets.get_issues(svc, "test_repo_id", "test_label")

    @patch("services.ZenhubService.ZenhubService.get_pipeline_id")
    def test_move_issues(self, mock_get_pipeline_id):
        mock_get_pipeline_id.return_value = "test_pipeline_id"
        svc = ZenhubService("123")
        svc.zenhub_client_gql_api = MagicMock()
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
        self.assertEqual(None, move_dependabot_tickets.move_issues(svc, issues, "test_pipeline_id"))

    def test_move_issues_without_pipeline_id(self):
        svc = ZenhubService("123")
        svc.zenhub_client_gql_api = MagicMock()
        svc.get_pipeline_id = MagicMock(return_value=None)
        issues = [{"id": "test_issue_id"}]
        with self.assertRaises(ValueError):
            move_dependabot_tickets.move_issues(svc, issues, "test_pipeline_id")

    @patch("services.ZenhubService.ZenhubService.get_pipeline_id")
    def test_move_issues_without_issue_id(self, mock_get_pipeline_id):
        mock_get_pipeline_id.return_value = "test_pipeline_id"
        svc = ZenhubService("123")
        svc.zenhub_client_gql_api = MagicMock()
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

        self.assertEqual(None, move_dependabot_tickets.move_issues(svc, issues, "test_pipeline_id"))


if __name__ == '__main__':
    unittest.main()
