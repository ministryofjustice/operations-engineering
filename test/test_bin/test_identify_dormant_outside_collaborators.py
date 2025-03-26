import unittest
from unittest.mock import MagicMock, patch

from bin.identify_dormant_outside_collaborators import identify_dormant_outside_collaborators

from services.github_service import GithubService
from services.slack_service import SlackService

class TestIdentifyDormantOutsideCollaborators(unittest.TestCase):

    def setUp(self):
        self.test_data_for_both_orgs = [
            [
                {'repository': 'repo1', 'public': False, 'outside_collaborators': ['oc1']},
                {'repository': 'repo2', 'public': False, 'outside_collaborators': ['oc1', 'oc2']}
            ],
            [
                {'repository': 'repo3', 'public': False, 'outside_collaborators': ['oc2']},

            ]
        ]

    @patch.object(GithubService, "__new__")
    @patch.object(SlackService, "__new__")
    @patch('os.environ')
    def test_all_outside_collaborators_dormant(self, mock_env, mock_slack_service, mock_github_service):
        mock_env.get.side_effect = lambda k: 'mock_token' if k in ['GH_MOJ_TOKEN', 'GH_MOJAS_TOKEN', 'ADMIN_SLACK_TOKEN'] else 90 if k in ['DAYS_SINCE'] else None

        mock_github_instance = MagicMock()
        mock_github_service.return_value = mock_github_instance
        mock_github_instance.get_active_repos_and_outside_collaborators.side_effect = self.test_data_for_both_orgs
        mock_github_instance.user_has_committed_to_repo_since.side_effect = [False, False, False, False]

        mock_slack_instance = MagicMock()
        mock_slack_service.return_value = mock_slack_instance

        identify_dormant_outside_collaborators()

        mock_slack_instance.send_dormant_outside_collaborator_list.assert_called()
        mock_slack_instance.send_dormant_outside_collaborator_list.assert_called_once_with(user_list=['oc1', 'oc2'], days_since='90')

    @patch.object(GithubService, "__new__")
    @patch.object(SlackService, "__new__")
    @patch('os.environ')
    def test_one_outside_collaborator_dormant(self, mock_env, mock_slack_service, mock_github_service):
        mock_env.get.side_effect = lambda k: 'mock_token' if k in ['GH_MOJ_TOKEN', 'GH_MOJAS_TOKEN', 'ADMIN_SLACK_TOKEN'] else 90 if k in ['DAYS_SINCE'] else None

        mock_github_instance = MagicMock()
        mock_github_service.return_value = mock_github_instance
        mock_github_instance.get_active_repos_and_outside_collaborators.side_effect = self.test_data_for_both_orgs
        mock_github_instance.user_has_committed_to_repo_since.side_effect = [False, True, False, False]

        mock_slack_instance = MagicMock()
        mock_slack_service.return_value = mock_slack_instance

        identify_dormant_outside_collaborators()

        mock_slack_instance.send_dormant_outside_collaborator_list.assert_called()
        mock_slack_instance.send_dormant_outside_collaborator_list.assert_called_once_with(user_list=['oc2'], days_since='90')

    @patch.object(GithubService, "__new__")
    @patch.object(SlackService, "__new__")
    @patch('os.environ')
    def test_active_in_all_repos_identifies_zero_dormant_ocs(self, mock_env, mock_slack_service, mock_github_service):
        mock_env.get.side_effect = lambda k: 'mock_token' if k in ['GH_MOJ_TOKEN', 'GH_MOJAS_TOKEN', 'ADMIN_SLACK_TOKEN'] else 90 if k in ['DAYS_SINCE'] else None

        mock_github_instance = MagicMock()
        mock_github_service.return_value = mock_github_instance
        mock_github_instance.get_active_repos_and_outside_collaborators.side_effect = self.test_data_for_both_orgs
        mock_github_instance.user_has_committed_to_repo_since.side_effect = [True, True, True, True]

        mock_slack_instance = MagicMock()
        mock_slack_service.return_value = mock_slack_instance

        identify_dormant_outside_collaborators()

        mock_slack_instance.send_dormant_outside_collaborator_list.assert_called()
        mock_slack_instance.send_dormant_outside_collaborator_list.assert_called_once_with(user_list=[], days_since='90')

    @patch.object(GithubService, "__new__")
    @patch.object(SlackService, "__new__")
    @patch('os.environ')
    def test_ocs_active_in_at_least_one_repo_identifies_zero_dormant_ocs(self, mock_env, mock_slack_service, mock_github_service):
        mock_env.get.side_effect = lambda k: 'mock_token' if k in ['GH_MOJ_TOKEN', 'GH_MOJAS_TOKEN', 'ADMIN_SLACK_TOKEN'] else 90 if k in ['DAYS_SINCE'] else None

        mock_github_instance = MagicMock()
        mock_github_service.return_value = mock_github_instance
        mock_github_instance.get_active_repos_and_outside_collaborators.side_effect = self.test_data_for_both_orgs
        mock_github_instance.user_has_committed_to_repo_since.side_effect = [False, True, True, False]

        mock_slack_instance = MagicMock()
        mock_slack_service.return_value = mock_slack_instance

        identify_dormant_outside_collaborators()

        mock_slack_instance.send_dormant_outside_collaborator_list.assert_called()
        mock_slack_instance.send_dormant_outside_collaborator_list.assert_called_once_with(user_list=[], days_since='90')


if __name__ == "__main__":
    unittest.main()
