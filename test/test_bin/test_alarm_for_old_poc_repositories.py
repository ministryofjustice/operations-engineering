import unittest
from unittest.mock import patch, MagicMock
from services.github_service import GithubService
from services.slack_service import SlackService
from bin.alarm_for_old_poc_repositories import alert_for_old_poc_repositories


class TestOldPOCGitHubRepositoriesAlerting(unittest.TestCase):

    @patch("gql.transport.aiohttp.AIOHTTPTransport.__new__", new=MagicMock)
    @patch("gql.Client.__new__", new=MagicMock)
    @patch("github.Github.__new__")
    @patch.object(GithubService, "get_old_poc_repositories")
    @patch.object(SlackService, "send_alert_for_poc_repositories")
    @patch('os.environ')
    def test_alert_for_old_poc_repositories_if_found(
        self,
        mock_env,
        mock_send_alert_for_poc_repositories,
        mock_get_old_poc_repositories,
        _mock_github_client_core_api
    ):
        mock_env.get.side_effect = lambda k: 'mock_token' if k in ['GH_TOKEN', 'ADMIN_SLACK_TOKEN'] else None
        mock_get_old_poc_repositories.return_value = {"repo1": 51, "repo2": 60}

        alert_for_old_poc_repositories()

        mock_get_old_poc_repositories.assert_called_once()
        mock_send_alert_for_poc_repositories.assert_called_once_with({
            "repo1": 51,
            "repo2": 60
        })

    @patch("gql.transport.aiohttp.AIOHTTPTransport.__new__", new=MagicMock)
    @patch("gql.Client.__new__", new=MagicMock)
    @patch("github.Github.__new__")
    @patch.object(GithubService, "get_old_poc_repositories")
    @patch.object(SlackService, "send_alert_for_poc_repositories")
    @patch('os.environ')
    def test_alert_for_old_poc_repositories_if_not_found(
        self,
        mock_env,
        mock_send_alert_for_poc_repositories,
        mock_get_old_poc_repositories,
        _mock_github_client_core_api
    ):
        mock_env.get.side_effect = lambda k: 'mock_token' if k in ['GH_TOKEN', 'ADMIN_SLACK_TOKEN'] else None
        mock_get_old_poc_repositories.return_value = {}

        alert_for_old_poc_repositories()

        mock_get_old_poc_repositories.assert_called_once()
        mock_send_alert_for_poc_repositories.assert_not_called()


if __name__ == '__main__':
    unittest.main()
