import unittest
from unittest.mock import patch, MagicMock

from bin.alert_on_low_github_licences import alert_on_low_github_licenses

from services.github_service import GithubService
from services.slack_service import SlackService


class TestGithubLicenseAlerting(unittest.TestCase):

    @patch.object(GithubService, "__new__")
    @patch.object(SlackService, "__new__")
    @patch('os.environ')
    def test_alert_on_low_github_licences(self, mock_env, mock_slack_service, mock_github_service):
        """ Test the alerting functionality for low GitHub licenses. """
        mock_env.get.side_effect = lambda k: 'mock_token' if k in [
            'ADMIN_GITHUB_TOKEN', 'ADMIN_SLACK_TOKEN'] else None

        mock_github_instance = MagicMock()
        mock_github_service.return_value = mock_github_instance
        mock_github_instance.get_remaining_licences.return_value = 5

        mock_slack_instance = MagicMock()
        mock_slack_service.return_value = mock_slack_instance

        alert_on_low_github_licenses()

        mock_slack_instance.send_low_github_licenses_alert.assert_called()


if __name__ == '__main__':
    unittest.main()
