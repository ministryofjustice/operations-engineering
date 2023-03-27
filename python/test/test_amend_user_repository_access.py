import unittest
from unittest.mock import patch

from python.scripts import amend_user_repository_access
from python.lib.organisation import Constants
from python.lib.organisation import Organisation
from python.services.github_service import GithubService


@patch.object(Constants, "__new__")
@patch.object(GithubService, "__new__")
@patch.object(Organisation, "__new__")
class TestAmendUserRepositoryAccess(unittest.TestCase):

    def test_main_smoke_test(self, mock1, mock2, mock3):
        amend_user_repository_access.main()


if __name__ == "__main__":
    unittest.main()
