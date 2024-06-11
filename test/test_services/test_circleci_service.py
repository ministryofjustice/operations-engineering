import unittest
from unittest.mock import patch, MagicMock
import yaml
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

    def test_get_all_pipeline_ids_for_all_repositories_success(self, _mock_get):
        repo_list = ["repo1", "repo2"]
        self.service.get_circleci_pipelines_for_repository = MagicMock()

        self.service.get_circleci_pipelines_for_repository.side_effect = [
            [{"id": "pipeline1"}, {"id": "pipeline2"}],
            [{"id": "pipeline3"}]
        ]

        all_pipeline_ids = self.service.get_all_pipeline_ids_for_all_repositories(repo_list, self.service)
        self.assertEqual(all_pipeline_ids, ["pipeline1", "pipeline2", "pipeline3"])

        self.service.get_circleci_pipelines_for_repository.assert_any_call("repo1")
        self.service.get_circleci_pipelines_for_repository.assert_any_call("repo2")

    def test_get_all_pipeline_ids_for_all_repositories_empty_repo_list(self, _mock_get):
        repo_list = []
        all_pipeline_ids = self.service.get_all_pipeline_ids_for_all_repositories(repo_list, self.service)
        self.assertEqual(all_pipeline_ids, [])

    def test_get_all_pipeline_ids_for_all_repositories_with_errors(self, _mock_get):
        repo_list = ["repo1", "repo2"]
        self.service.get_circleci_pipelines_for_repository = MagicMock()

        self.service.get_circleci_pipelines_for_repository.side_effect = [
            [{"id": "pipeline1"}],
            []
        ]

        all_pipeline_ids = self.service.get_all_pipeline_ids_for_all_repositories(repo_list, self.service)
        self.assertEqual(all_pipeline_ids, ["pipeline1"])

        self.service.get_circleci_pipelines_for_repository.assert_any_call("repo1")
        self.service.get_circleci_pipelines_for_repository.assert_any_call("repo2")

    def test_get_all_used_contexts_success(self, _mock_get):
        pipeline_id_list = ["pipeline1", "pipeline2"]
        self.service.get_pipeline_configurations_from_pipeline_id = MagicMock()
        self.service.find_all_contexts_from_configuration = MagicMock()

        self.service.get_pipeline_configurations_from_pipeline_id.side_effect = [
            {"compiled": "compiled_config_data1", "compiled-setup-config": "compiled_setup_config_data1"},
            {"compiled": "compiled_config_data2", "compiled-setup-config": "compiled_setup_config_data2"}
        ]
        self.service.find_all_contexts_from_configuration.side_effect = [
            ["context1", "context2"],
            [],
            ["context3"],
            []
        ]

        all_used_contexts = self.service.get_all_used_contexts(pipeline_id_list)
        self.assertEqual(all_used_contexts, {"context1", "context2", "context3"})

        self.service.get_pipeline_configurations_from_pipeline_id.assert_any_call("pipeline1")
        self.service.get_pipeline_configurations_from_pipeline_id.assert_any_call("pipeline2")
        self.service.find_all_contexts_from_configuration.assert_any_call(yaml.safe_load("compiled_config_data1"))
        self.service.find_all_contexts_from_configuration.assert_any_call(yaml.safe_load("compiled_setup_config_data1"))
        self.service.find_all_contexts_from_configuration.assert_any_call(yaml.safe_load("compiled_config_data2"))
        self.service.find_all_contexts_from_configuration.assert_any_call(yaml.safe_load("compiled_setup_config_data2"))

    def test_get_all_used_contexts_with_empty_configs(self, _mock_get):
        pipeline_id_list = ["pipeline1", "pipeline2"]
        self.service.get_pipeline_configurations_from_pipeline_id = MagicMock()
        self.service.find_all_contexts_from_configuration = MagicMock()

        self.service.get_pipeline_configurations_from_pipeline_id.side_effect = [
            {"compiled": "compiled_config_data1", "compiled-setup-config": ""},
            {}
        ]
        self.service.find_all_contexts_from_configuration.side_effect = [
            ["context1", "context2"],
            []
        ]

        all_used_contexts = self.service.get_all_used_contexts(pipeline_id_list)
        self.assertEqual(all_used_contexts, {"context1", "context2"})

        self.service.get_pipeline_configurations_from_pipeline_id.assert_any_call("pipeline1")
        self.service.get_pipeline_configurations_from_pipeline_id.assert_any_call("pipeline2")
        self.service.find_all_contexts_from_configuration.assert_any_call(yaml.safe_load("compiled_config_data1"))


if __name__ == "__main__":
    unittest.main()
