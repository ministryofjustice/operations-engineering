import unittest
from unittest.mock import patch, MagicMock
from services.circleci_service import CircleciService


@patch("requests.get")
class TestCircleciService(unittest.TestCase):
    def setUp(self):
        self.token = "test_token"
        self.owner_id = "test_owner_id"
        self.github_org = "test_org"
        self.service = CircleciService(self.token, self.owner_id, self.github_org)

    def test_get_circleci_pipelines_for_repository_success(self, mock_get):
        repo = "test_repo"
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": [{"id": "pipeline1"}, {"id": "pipeline2"}]}
        mock_get.return_value = mock_response

        pipelines = self.service.get_circleci_pipelines_for_repository(repo)
        self.assertEqual(len(pipelines), 2)
        self.assertEqual(pipelines[0]["id"], "pipeline1")
        self.assertEqual(pipelines[1]["id"], "pipeline2")

        url = f"https://circleci.com/api/v2/project/github/{self.github_org}/{repo}/pipeline"
        mock_get.assert_called_once_with(url, headers=self.service.headers, timeout=60)

    def test_get_circleci_pipelines_for_repository_failure(self, mock_get):
        repo = "test_repo"
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_get.return_value = mock_response

        pipelines = self.service.get_circleci_pipelines_for_repository(repo)
        self.assertEqual(pipelines, [])

    def test_get_pipeline_configurations_from_pipeline_id_success(self, mock_get):
        pipeline_id = "test_pipeline_id"
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"config": "config_data"}
        mock_get.return_value = mock_response

        config = self.service.get_pipeline_configurations_from_pipeline_id(pipeline_id)
        self.assertEqual(config, {"config": "config_data"})

        url = self.service.base_url + f"pipeline/{pipeline_id}/config"
        mock_get.assert_called_once_with(url, headers=self.service.headers, timeout=60)

    def test_get_pipeline_configurations_from_pipeline_id_failure(self, mock_get):
        pipeline_id = "test_pipeline_id"
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_get.return_value = mock_response

        config = self.service.get_pipeline_configurations_from_pipeline_id(pipeline_id)
        self.assertEqual(config, {})

    def test_find_all_contexts_from_configuration(self, _mock_get):
        configuration = {
            "jobs": [
                {
                    "steps": [
                        {"checkout": {}},
                        {"run": {"name": "Test", "command": "echo 'Test'", "context": ["context1", "context2"]}},
                    ]
                }
            ],
            "workflows": {
                "version": 2,
                "build_and_test": {
                    "jobs": [
                        {"build": {"context": "context3"}}
                    ]
                }
            }
        }
        contexts = self.service.find_all_contexts_from_configuration(configuration)
        self.assertEqual(len(contexts), 3)
        self.assertIn("context1", contexts)
        self.assertIn("context2", contexts)
        self.assertIn("context3", contexts)

    def test_list_all_contexts_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = [
            {"items": [{"name": "context1"}, {"name": "context2"}], "next_page_token": "next_page"},
            {"items": [{"name": "context3"}], "next_page_token": None}
        ]
        mock_get.return_value = mock_response

        contexts = self.service.list_all_contexts()
        self.assertEqual(len(contexts), 3)
        self.assertIn("context1", contexts)
        self.assertIn("context2", contexts)
        self.assertIn("context3", contexts)

        url = self.service.base_url + f"context?owner-id={self.owner_id}"
        headers = self.service.headers

        mock_get.assert_any_call(url, headers=headers, params={}, timeout=360)
        mock_get.assert_any_call(url, headers=headers, params={'page-token': 'next_page'}, timeout=360)
        self.assertEqual(mock_get.call_count, 2)

    def test_list_all_contexts_failure(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_get.return_value = mock_response

        contexts = self.service.list_all_contexts()
        self.assertEqual(contexts, [])


if __name__ == "__main__":
    unittest.main()
