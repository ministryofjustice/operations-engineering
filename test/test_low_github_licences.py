import unittest
from unittest.mock import patch, MagicMock

from bin.alert_on_low_github_licences import low_theshold_triggered_message, alert_on_low_github_licences

from services.github_service import GithubService
from services.slack_service import SlackService


class TestGithubLicenseAlerting(unittest.TestCase):

    def test_low_threshold_triggered_message(self):
        """ Test the message format for low threshold alert. """
        remaining_licences = 5
        expected_message = (
            "Hi team 👋, \n\n"
            "There are only 5     GitHub licences remaining in the enterprise account. \n\n"
            "Please add more licences to the enterprise account. \n\n"
            "Thanks, \n\n"
            "The GitHub Licence Alerting Bot"
        )
        self.assertEqual(low_theshold_triggered_message(
            remaining_licences), expected_message)

    @patch.object(GithubService, "__new__")
    @patch.object(SlackService, "__new__")
    @patch('os.environ')
    def test_alert_on_low_github_licences(self, mock_env, mock_slack_service, mock_github_service):
        """ Test the alerting functionality for low GitHub licenses. """
        mock_env.get.side_effect = lambda k: 'mock_token' if k in [
            'GITHUB_TOKEN', 'SLACK_TOKEN'] else None

        mock_github_instance = MagicMock()
        mock_github_service.return_value = mock_github_instance
        mock_github_instance.get_remaining_licences.return_value = 5

        mock_slack_instance = MagicMock()
        mock_slack_service.return_value = mock_slack_instance

        alert_on_low_github_licences(10)

        mock_slack_instance.send_message_to_plaintext_channel_name.assert_called()


if __name__ == '__main__':
    unittest.main()
