import unittest
from unittest.mock import patch, MagicMock

from .ZenhubService import ZenhubService


@patch("gql.Client.__new__", new=MagicMock)
@patch("gql.transport.aiohttp.AIOHTTPTransport.__new__", new=MagicMock)
class TestZenhubService(unittest.TestCase):

    def test_sets_up_class(self):
        svc = ZenhubService("123")
        self.assertIsNone(svc._workspace_id)
        self.assertIsNotNone(svc.zenhub_client_gql_api)

        svc._workspace_id = "test_workspace_id"
        self.assertEqual("test_workspace_id", svc._workspace_id)


@patch("gql.Client.__new__", new=MagicMock)
@patch("gql.transport.aiohttp.AIOHTTPTransport.__new__", new=MagicMock)
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
                                "id": 12
                            }
                        ]
                    }
                }
            ]
        }
        workspace_id = mock.get_workspace_id_from_repo(12)
        self.assertEqual(12, workspace_id)

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
        mock_zenhub_service = ZenhubService("123")
        mock_zenhub_service.zenhub_client_gql_api.execute.return_value = {
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
        pipeline_id = mock_zenhub_service.get_pipeline_id("test_pipeline_name")
        self.assertEqual("test_pipeline_id", pipeline_id)

        # Sad path
        false_pipeline_id = mock_zenhub_service.get_pipeline_id(
            "test_pipeline_name_false")
        self.assertEqual(None, false_pipeline_id)


@patch("gql.Client.__new__", new=MagicMock)
@patch("gql.transport.aiohttp.AIOHTTPTransport.__new__", new=MagicMock)
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
        issue_id = svc.move_issue_to_pipeline(
            "test_issue_id", "pipeline_issue_id")
        self.assertEqual(True, issue_id)

        bad_search = svc.move_issue_to_pipeline(
            "test_issue_id", "wrong_pipeline_issue_id")
        self.assertEqual(False, bad_search)
