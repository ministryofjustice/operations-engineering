import os
import unittest
from unittest.mock import patch, MagicMock
from services.github_service import GithubService

from bin.remove_stale_outside_collaborators import(
    main,
    get_environment_variables
)

@patch("bin.remove_stale_outside_collaborators.GithubService", new=MagicMock)
@patch("github.Github.__new__", new=MagicMock)
# @patch("gql.Client.__new__", new=MagicMock)
# @patch("gql.transport.aiohttp.AIOHTTPTransport.__new__", new=MagicMock)
@patch.dict(os.environ, {"ADMIN_GITHUB_TOKEN": "token"})
class TestRemoveStaleOutsideCollaboratorsMain(unittest.TestCase):
    def setUp(self):
        self.stale_outside_collaborators = [
            "stale_outside_collab_1", "stale_outside_collab_2"
        ]

    def test_main_logs_info(self):
        github = GithubService("", "test_org")
        org = MagicMock()
        org.return_value.organisation_name.return_value = "test_org"
        # github.organisation_name = MagicMock(
        #     return_value="test_org"
        # )
        github.get_stale_outside_collaborators = MagicMock(
            return_value=self.stale_outside_collaborators
        )

        main()
        self.assertLogs()
