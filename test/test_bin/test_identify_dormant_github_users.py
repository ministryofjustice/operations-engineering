import unittest
from unittest.mock import MagicMock, patch

from bin.identify_dormant_github_users import (
    ALLOWED_BOT_USERS,
    get_dormant_users_from_data_lake,
    get_inactive_users_from_data_lake_ignoring_bots_and_collaborators)

from services.cloudtrail_service import CloudtrailService

class TestDormantGitHubUsers(unittest.TestCase):

    def setUp(self):
        self.allowed_bot_users = ["bot1", "bot2"]

    @patch('bin.identify_dormant_github_users.get_inactive_users_from_data_lake_ignoring_bots_and_collaborators')
    @patch('services.dormant_github_user_service.DormantGitHubUser')
    @patch('services.github_service.GithubService')
    def test_get_dormant_users_from_data_lake(self, mock_github_service, mock_dormant_github_user, mock_get_inactive_users_from_data_lake_ignoring_bots_and_collaborators):
        mock_get_inactive_users_from_data_lake_ignoring_bots_and_collaborators.return_value = ['user1', 'user2', 'user3']
        github_service = mock_github_service
        mock_dormant_github_user.side_effect = lambda github_service, user: MagicMock(__str__=lambda: f'DormantGitHubUser({user})')

        result = get_dormant_users_from_data_lake(github_service)

        self.assertEqual(len(result), 3)
        mock_get_inactive_users_from_data_lake_ignoring_bots_and_collaborators.assert_called_once_with(github_service, ALLOWED_BOT_USERS)

    @patch.object(CloudtrailService, "get_active_users_for_dormant_users_process")
    def test_get_inactive_users_from_data_lake_ignoring_bots_and_collaborators(self, mock_get_active_users_for_dormant_users_process):
        mock_get_active_users_for_dormant_users_process.return_value = ["member1"]
        mock_github_service = MagicMock()
        mock_github_service.get_all_enterprise_members = MagicMock(return_value=["member1", "member2", "bot1", "bot2"])

        assert get_inactive_users_from_data_lake_ignoring_bots_and_collaborators(mock_github_service, self.allowed_bot_users) == ["member2"]


if __name__ == '__main__':
    unittest.main()
