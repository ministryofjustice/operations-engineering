import unittest
from unittest.mock import patch

from github import Github

import archive_repositories


@patch.object(Github, "__new__")
class TestArchiveRepositories(unittest.TestCase):

    @patch("sys.argv", ["", "test"])
    def test_main_smoke_test(self, mock_github):
        archive_repositories.main()


if __name__ == "__main__":
    unittest.main()
