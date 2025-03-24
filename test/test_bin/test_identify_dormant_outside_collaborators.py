import unittest
from unittest.mock import MagicMock, patch

from bin.identify_dormant_outside_collaborators import identify_dormant_outside_collaborators


class TestIdentifyDormantOutsideCollaborators(unittest.TestCase):

    @patch("gql.transport.aiohttp.AIOHTTPTransport.__new__", new=MagicMock)
    @patch("gql.Client.__new__", new=MagicMock)
    @patch("services.github_service.Github")
    @patch('os.environ')
    def test_identify_dormant_outside_collaborators(self, mock_env, mock_get_active_repos_and_outside_collaborators, mock_user_has_committed_to_repo_since):
        mock_env.get.side_effect = lambda k: 'mock_token' if k in ['GH_MOJ_TOKEN', 'GH_MOJAS_TOKEN', 'ADMIN_SLACK_TOKEN'] else 90 if k in ['DAYS_SINCE'] else None
        mock_get_active_repos_and_outside_collaborators.return_value = [
            {'repository': 'repo1', 'public': False, 'outside_collaborators': ['outside_collab_1', 'outside_collab_2']},
            {'repository': 'repo2', 'public': True, 'outside_collaborators': ['outside_collab_3']}
        ]
        mock_user_has_committed_to_repo_since.return_value = [True, False, True]

        identify_dormant_outside_collaborators()

        mock_get_active_repos_and_outside_collaborators.assert_called_once()


if __name__ == "__main__":
    unittest.main()
