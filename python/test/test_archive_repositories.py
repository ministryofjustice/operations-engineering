import os
import unittest
from unittest.mock import patch

from github import Github

from python.scripts import archive_repositories


@patch.object(Github, "__new__")
class TestArchiveRepositories(unittest.TestCase):

    @patch.dict(os.environ, {"ADMIN_GITHUB_TOKEN": "token"})
    def test_main_smoke_test(self, mock_github):
        archive_repositories.main()

    def test_main_returns_error_when_no_token_provided(self, mock_github):
        self.assertRaises(
            ValueError, archive_repositories.main)


if __name__ == "__main__":
    unittest.main()
