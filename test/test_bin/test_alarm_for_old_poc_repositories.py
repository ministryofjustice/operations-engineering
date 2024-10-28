import unittest
from unittest.mock import patch, MagicMock

from bin.alarm_for_old_poc_repositories import (
    construct_message,
    alert_for_old_poc_repositories
)

from services.github_service import GithubService
from services.slack_service import SlackService


class TestOldPOCGitHubRepositoriesAlerting(unittest.TestCase):

    def test_construct_message(self):
        test_payload = {"repo1": 51, "repo2": 60}

        self.assertEqual(construct_message(test_payload), "The following POC GitHub Repositories persist:\n\nhttps://github.com/ministryofjustice/repo1 - 51 days old\nhttps://github.com/ministryofjustice/repo2 - 60 days old\n\nConsider if they are still required. If not, please archive them by removing them from the Terraform configuration: https://github.com/ministryofjustice/operations-engineering/tree/main/terraform/github/repositories/ministryofjustice")

    @patch("gql.transport.aiohttp.AIOHTTPTransport.__new__", new=MagicMock)
    @patch("gql.Client.__new__", new=MagicMock)
    @patch("github.Github.__new__")
    @patch("bin.alarm_for_old_poc_repositories.construct_message")
    @patch.object(GithubService, "get_old_poc_repositories")
    @patch.object(SlackService, "send_message_to_plaintext_channel_name")
    @patch('os.environ')
    def test_alert_for_old_poc_repositories_if_found(
        self,
        mock_env,
        mock_send_message_to_plaintext_channel_name,
        mock_get_old_poc_repositories,
        mock_construct_message,
        _mock_github_client_core_api
    ):

        mock_env.get.side_effect = lambda k: 'mock_token' if k in ['GH_TOKEN', 'ADMIN_SLACK_TOKEN'] else None
        mock_get_old_poc_repositories.return_value = {"repo1": 51, "repo2": 60}
        mock_construct_message.return_value = "The following POC GitHub Repositories persist:\n\nhttps://github.com/ministryofjustice/repo1 - 51 days old\nhttps://github.com/ministryofjustice/repo2 - 60 days old\n\nConsider if they are still required. If not, please archive them by removing them from the Terraform configuration: https://github.com/ministryofjustice/operations-engineering/tree/main/terraform/github/repositories/ministryofjustice"

        alert_for_old_poc_repositories()

        mock_get_old_poc_repositories.assert_called_once()
        mock_send_message_to_plaintext_channel_name.assert_called_once_with("The following POC GitHub Repositories persist:\n\nhttps://github.com/ministryofjustice/repo1 - 51 days old\nhttps://github.com/ministryofjustice/repo2 - 60 days old\n\nConsider if they are still required. If not, please archive them by removing them from the Terraform configuration: https://github.com/ministryofjustice/operations-engineering/tree/main/terraform/github/repositories/ministryofjustice", "operations-engineering-alerts")

    @patch("gql.transport.aiohttp.AIOHTTPTransport.__new__", new=MagicMock)
    @patch("gql.Client.__new__", new=MagicMock)
    @patch("github.Github.__new__")
    @patch.object(GithubService, "get_old_poc_repositories")
    @patch.object(SlackService, "send_message_to_plaintext_channel_name")
    @patch('os.environ')
    def test_alert_for_old_poc_repositories_if_not_found(
        self,
        mock_env,
        mock_send_message_to_plaintext_channel_name,
        mock_get_old_poc_repositories,
        _mock_github_client_core_api
    ):

        mock_env.get.side_effect = lambda k: 'mock_token' if k in ['GH_TOKEN', 'ADMIN_SLACK_TOKEN'] else None
        mock_get_old_poc_repositories.return_value = {}

        alert_for_old_poc_repositories()

        mock_get_old_poc_repositories.assert_called_once()
        assert not mock_send_message_to_plaintext_channel_name.called


if __name__ == '__main__':
    unittest.main()
