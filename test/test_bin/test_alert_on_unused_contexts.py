import unittest

from unittest.mock import patch
from bin.alert_on_unused_contexts import main


class TestMainScript(unittest.TestCase):

    def setUp(self):
        self.repo_list = ["repo1", "repo2"]
        self.pipeline_ids = ["pipeline1", "pipeline2"]
        self.used_contexts = {"context1", "context2"}
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
        mock_circleci_instance.get_all_pipeline_ids_for_all_repositories.return_value = self.pipeline_ids
        mock_circleci_instance.get_all_used_contexts.return_value = self.used_contexts
        mock_circleci_instance.list_all_contexts.return_value = self.all_contexts

        mock_slack_instance = mock_slack_service.return_value

        main()

        mock_github_instance.check_circleci_config_in_repos.assert_called_once()
        mock_circleci_instance.get_all_pipeline_ids_for_all_repositories.assert_called_once_with(self.repo_list, mock_circleci_instance)
        mock_circleci_instance.get_all_used_contexts.assert_called_once_with(self.pipeline_ids)
        mock_circleci_instance.list_all_contexts.assert_called_once()
        mock_slack_instance.send_unused_circleci_context_alert_to_operations_engineering.assert_called_once_with(1)


if __name__ == "__main__":
    unittest.main()
