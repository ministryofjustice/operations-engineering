import unittest
from unittest.mock import patch, MagicMock

from .ZenhubService import ZenhubService


@patch("gql.Client.__new__")
class TestZenhubService(unittest.TestCase):

    def test_sets_up_class(self, mock_gql_client):
        mock_gql_client.return_value = "test_mock_gql_client"
        svc = ZenhubService("123")
        self.assertIsNone(svc._workspace_id)
        self.assertEqual("test_mock_gql_client", svc.zenhub_client_gql_api)

        svc._workspace_id = "test_workspace_id"
        self.assertEqual("test_workspace_id", svc._workspace_id)


class TestZenhubIssueRetrieval(unittest.TestCase):
    def test_gets_workspace_from_repo(self):
        mock = ZenhubService("123")
        mock.zenhub_client_gql_api = MagicMock()
        mock.zenhub_client_gql_api.execute.return_value = {
            "repositoriesByGhId":
            [
                {
                    "workspacesConnection": {
                        "nodes": [
                            {
                                "id": "test_workspace_id"
                            }
                        ]
                    }
                }
            ]
        }
        workspace_id = mock.get_workspace_id_from_repo("test_repo_id")
        self.assertEqual("test_workspace_id", workspace_id)

    def test_returns_none_when_no_workspace_found(self):
        svc = ZenhubService("123")
        svc.zenhub_client_gql_api = MagicMock()
        svc.zenhub_client_gql_api.execute.return_value = {
            "repositoriesByGhId":
            [
                {
                    "workspacesConnection": {
                        "nodes": [
                        ]
                    }
                }
            ]
        }
        workspace_id = svc.get_workspace_id_from_repo("test_repo_id")
        self.assertRaises(Exception, workspace_id)

    def test_search_issue_by_label(self):
        svc = ZenhubService("123")
        svc.zenhub_client_gql_api = MagicMock()
        svc.zenhub_client_gql_api.execute.return_value = {
            "searchIssuesByPipeline": {
                "nodes": [
                    {
                        "id": "test_issue_id"
                    }
                ]
            }
        }
        issue_id = svc.search_issues_by_label("test_pipeline_id", "test_label")
        self.assertEqual([{'id': 'test_issue_id'}], issue_id)

    def test_search_issue_by_label_returns_none_when_no_issues_found(self):
        svc = ZenhubService("123")
        svc.zenhub_client_gql_api = MagicMock()
        svc.zenhub_client_gql_api.execute.return_value = {
            "searchIssuesByPipeline": {
                "nodes": [
                ]
            }
        }
        issue_id = svc.search_issues_by_label("test_pipeline_id", "test_label")
        self.assertEqual([], issue_id)

    def test_get_pipeline_id(self):
        svc = ZenhubService("123")
        svc.zenhub_client_gql_api = MagicMock()
        svc.zenhub_client_gql_api.execute.return_value = {
            "workspace": {
                "pipelinesConnection": {
                    "nodes": [
                        {
                            "id": "test_pipeline_id",
                            "name": "test_pipeline_name"
                        }
                    ]
                }
            }
        }
        # Happy path
        pipeline_id = svc.get_pipeline_id("test_pipeline_name")
        self.assertEqual("test_pipeline_id", pipeline_id)

        # Sad path
        false_pipeline_id = svc.get_pipeline_id("test_pipeline_name_false")
        self.assertEqual(None, false_pipeline_id)


class TestZenhubMovingIssues(unittest.TestCase):
    def test_move_issue_to_pipeline(self):
        svc = ZenhubService("123")
        svc.zenhub_client_gql_api = MagicMock()
        svc.zenhub_client_gql_api.execute.return_value = {
            "moveIssue": {
                "issue": {
                    "id": "issue_id",
                    "pipelineIssue": {
                        "pipeline": {
                            "id": "pipeline_issue_id"
                        }
                    }
                }
            }
        }
        issue_id = svc.move_issue_to_pipeline("test_issue_id", "pipeline_issue_id")
        self.assertEqual(True, issue_id)

        bad_search = svc.move_issue_to_pipeline("test_issue_id", "wrong_pipeline_issue_id")
        self.assertEqual(False, bad_search)
