# pylint: disable=C0411

import os
import unittest
from unittest.mock import call, patch, MagicMock
from github import GithubException
from bin.remove_stale_outside_collaborators import main, get_environment_variables


class TestGetEnvironmentVariables(unittest.TestCase):
    @patch.dict(os.environ, {"ADMIN_GITHUB_TOKEN": "token", "GITHUB_ORGANIZATION_NAME": "test_org"})
    def test_returns_variables(self):
        github_token, github_organization_name = get_environment_variables()
        self.assertEqual(github_token, "token")
        self.assertEqual(github_organization_name, "test_org")

    @patch.dict(os.environ, {"GITHUB_ORGANIZATION_NAME": "test_org"})
    def test_raises_error_when_no_github_token(self):
        self.assertRaises(
            ValueError, get_environment_variables)

    @patch.dict(os.environ, {"ADMIN_GITHUB_TOKEN": "token"})
    def test_raises_error_when_no_github_org_name(self):
        self.assertRaises(
            ValueError, get_environment_variables)


@patch("services.github_service.GithubService.__new__")
@patch.dict(os.environ, {"ADMIN_GITHUB_TOKEN": "token", "GITHUB_ORGANIZATION_NAME": "test_org"})
class TestRemoveStaleOutsideCollaboratorsMain(unittest.TestCase):

    def test_main_remove_expected_number_of_outside_collaborators(self, mock_github_service: MagicMock):
        mock_github_service.return_value.get_stale_outside_collaborators.return_value = [
            "stale_outside_collab_1", "stale_outside_collab_2"
        ]
        main()
        mock_github_service.return_value.remove_outside_collaborator_from_org.assert_has_calls(
            [call('stale_outside_collab_1'), call('stale_outside_collab_2')]
        )

    def test_main_empty_stale_outside_collaborators(self, mock_github_service: MagicMock):
        mock_github_service.return_value.get_stale_outside_collaborators.return_value = []
        main()
        mock_github_service.return_value.remove_outside_collaborator_from_org.assert_not_called()

    def test_main_continues_after_exception(self, mock_github_service: MagicMock):
        mock_github_service.return_value.get_stale_outside_collaborators.return_value = [
            "stale_outside_collab_1", "stale_outside_collab_2"
        ]
        mock_github_service.return_value.remove_outside_collaborator_from_org.side_effect = GithubException(2)
        main()
        mock_github_service.return_value.remove_outside_collaborator_from_org.assert_has_calls(
            [call('stale_outside_collab_1'), call('stale_outside_collab_2')]
        )

    def test_main_exits_on_other_error(self, mock_github_service: MagicMock):
        mock_github_service.return_value.get_stale_outside_collaborators.return_value = [
            "stale_outside_collab_1", "stale_outside_collab_2"
        ]
        mock_github_service.return_value.remove_outside_collaborator_from_org.side_effect = ValueError()
        try:
            main()
        except ValueError:
            mock_github_service.return_value.remove_outside_collaborator_from_org.assert_has_calls(
                [call('stale_outside_collab_1')]
            )
