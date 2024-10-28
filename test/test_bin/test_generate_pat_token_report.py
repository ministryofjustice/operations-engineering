import unittest
from unittest.mock import patch
from bin.generate_pat_token_report import generate_pat_token_report, count_expired_tokens

from services.github_service import GithubService
from services.slack_service import SlackService


class TestPATTokenMonitoring(unittest.TestCase):

    def test_count_expired_tokens(self):
        """Test counting of expired tokens."""
        pat_tokens = [
            {'token_expired': True},
            {'token_expired': False},
            {'token_expired': True}
        ]
        self.assertEqual(count_expired_tokens(pat_tokens), 2)

    @patch.dict('os.environ', {'ADMIN_SLACK_TOKEN': 'mock_slack_token', 'GH_APP_TOKEN': 'mock_gh_token'})
    @patch('bin.generate_pat_token_report.count_expired_tokens')
    @patch.object(GithubService, "__new__")
    @patch.object(GithubService, 'get_new_pat_creation_events_for_organization')
    @patch.object(SlackService, 'send_pat_report_alert')
    def test_main_expired_tokens_found(self, mock_send_message, mock_get_pat_events, _mock_github_service, mock_count_expired_tokens):
        mock_get_pat_events.return_value = [{'token_expired': True}, {'token_expired': True}]
        mock_count_expired_tokens.return_value = 2

        generate_pat_token_report()

        mock_send_message.assert_called_once()

    @patch.dict('os.environ', {'ADMIN_SLACK_TOKEN': 'mock_slack_token', 'GH_APP_TOKEN': 'mock_gh_token'})
    @patch('bin.generate_pat_token_report.count_expired_tokens')
    @patch.object(GithubService, "__new__")
    @patch.object(GithubService, 'get_new_pat_creation_events_for_organization')
    @patch.object(SlackService, 'send_pat_report_alert')
    def test_main_no_expired_tokens_found(self, mock_send_message, mock_get_pat_events, _mock_github_service, mock_count_expired_tokens):
        mock_get_pat_events.return_value = [{'token_expired': False}, {'token_expired': False}]
        mock_count_expired_tokens.return_value = 0

        generate_pat_token_report()

        mock_send_message.assert_not_called()


if __name__ == '__main__':
    unittest.main()
