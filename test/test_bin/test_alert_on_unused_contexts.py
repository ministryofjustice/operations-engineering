import unittest

from unittest.mock import patch
from bin.alert_on_unused_contexts import main, get_all_pipeline_ids_for_all_repositories


class TestMainScript(unittest.TestCase):

    def setUp(self):
        self.repo_list = ["repo1", "repo2"]
        self.pipeline_ids = ["pipeline1", "pipeline2"]
        self.compiled_config = "compiled_config_data"
        self.compiled_setup_config = "compiled_setup_config_data"
        self.contexts = ["context1", "context2"]
        self.all_contexts = ["context1", "context2", "context3"]

    @patch.dict('os.environ', {
        'ADMIN_SLACK_TOKEN': 'test_slack_token',
        'ADMIN_GITHUB_TOKEN': 'test_github_token',
        'ADMIN_CIRCLECI_TOKEN': 'test_circleci_token',
        'CIRCLE_CI_OWNER_ID': 'test_owner_id'
    })
    @patch('bin.alert_on_unused_contexts.GithubService')
    @patch('bin.alert_on_unused_contexts.CircleciService')
    @patch('bin.alert_on_unused_contexts.SlackService')
    def test_main_script_logic(self, mock_slack_service, mock_circleci_service, mock_github_service):
        mock_github_instance = mock_github_service.return_value
        mock_github_instance.check_circleci_config_in_repos.return_value = self.repo_list

        mock_circleci_instance = mock_circleci_service.return_value
        mock_circleci_instance.get_circleci_pipelines_for_repository.side_effect = [
            [{"id": self.pipeline_ids[0]}],
            [{"id": self.pipeline_ids[1]}]
        ]
        mock_circleci_instance.get_pipeline_configurations_from_pipeline_id.side_effect = [
            {"compiled": self.compiled_config, "compiled-setup-config": self.compiled_setup_config},
            {}
        ]
        mock_circleci_instance.find_all_contexts_from_configuration.side_effect = [
            self.contexts,
            []
        ]
        mock_circleci_instance.list_all_contexts.return_value = self.all_contexts

        mock_slack_instance = mock_slack_service.return_value

        main()

        mock_github_instance.check_circleci_config_in_repos.assert_called_once()
        mock_circleci_instance.get_circleci_pipelines_for_repository.assert_any_call(self.repo_list[0])
        mock_circleci_instance.get_circleci_pipelines_for_repository.assert_any_call(self.repo_list[1])
        mock_circleci_instance.get_pipeline_configurations_from_pipeline_id.assert_any_call(self.pipeline_ids[0])
        mock_circleci_instance.get_pipeline_configurations_from_pipeline_id.assert_any_call(self.pipeline_ids[1])
        mock_circleci_instance.list_all_contexts.assert_called_once()
        mock_slack_instance.send_unused_circleci_context_alert_to_operations_engineering.assert_called_once_with(1)

    @patch('bin.alert_on_unused_contexts.CircleciService')
    def test_get_all_pipeline_ids_for_all_repositories(self, mock_circleci_service):
        mock_circleci_instance = mock_circleci_service.return_value
        mock_circleci_instance.get_circleci_pipelines_for_repository.side_effect = [
            [{"id": self.pipeline_ids[0]}],
            [{"id": self.pipeline_ids[1]}]
        ]

        pipeline_ids = get_all_pipeline_ids_for_all_repositories(self.repo_list, mock_circleci_instance)
        self.assertEqual(pipeline_ids, self.pipeline_ids)


if __name__ == '__main__':
    unittest.main()
