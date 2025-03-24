import unittest
from unittest.mock import MagicMock, patch

from bin.identify_dormant_outside_collaborators import identify_dormant_outside_collaborators

from services.github_service import GithubService
from services.slack_service import SlackService

class TestIdentifyDormantOutsideCollaborators(unittest.TestCase):

    @patch.object(GithubService, "__new__")
    @patch.object(SlackService, "__new__")
    @patch('os.environ')
    def test_identify_non_active_outside_collaborators(self, mock_env, mock_slack_service, mock_github_service):
        mock_env.get.side_effect = lambda k: 'mock_token' if k in ['GH_MOJ_TOKEN', 'GH_MOJAS_TOKEN', 'ADMIN_SLACK_TOKEN'] else 90 if k in ['DAYS_SINCE'] else None

        mock_github_instance = MagicMock()
        mock_github_service.return_value = mock_github_instance
        mock_github_instance.get_active_repos_and_outside_collaborators.return_value = [
            {'repository': 'repo1', 'public': False, 'outside_collaborators': ['outside_collab_1']}
        ]
        mock_github_instance.user_has_committed_to_repo_since.return_value = False

        mock_slack_instance = MagicMock()
        mock_slack_service.return_value = mock_slack_instance

        identify_dormant_outside_collaborators()

        mock_slack_instance.send_dormant_outside_collaborator_list.assert_called()
        mock_slack_instance.send_dormant_outside_collaborator_list.assert_called_once_with(user_list=['outside_collab_1'], days_since='90')

    @patch.object(GithubService, "__new__")
    @patch.object(SlackService, "__new__")
    @patch('os.environ')
    def test_ignore_active_outside_collaborators(self, mock_env, mock_slack_service, mock_github_service):
        mock_env.get.side_effect = lambda k: 'mock_token' if k in ['GH_MOJ_TOKEN', 'GH_MOJAS_TOKEN', 'ADMIN_SLACK_TOKEN'] else 90 if k in ['DAYS_SINCE'] else None

        mock_github_instance = MagicMock()
        mock_github_service.return_value = mock_github_instance
        mock_github_instance.get_active_repos_and_outside_collaborators.return_value = [
            {'repository': 'repo1', 'public': False, 'outside_collaborators': ['outside_collab_1']}
        ]
        mock_github_instance.user_has_committed_to_repo_since.return_value = True

        mock_slack_instance = MagicMock()
        mock_slack_service.return_value = mock_slack_instance

        identify_dormant_outside_collaborators()

        mock_slack_instance.send_dormant_outside_collaborator_list.assert_called()
        mock_slack_instance.send_dormant_outside_collaborator_list.assert_called_once_with(user_list=[], days_since='90')


if __name__ == "__main__":
    unittest.main()
