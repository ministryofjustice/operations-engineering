import unittest
from unittest.mock import patch

# Needed to mock the objects in the GithubService class
from github import Github
from gql import Client
from gql.transport.aiohttp import AIOHTTPTransport

from python.scripts import amend_user_repository_access
from python.lib.constants import Constants
from python.lib.organisation import Organisation

# Needed to mock the objects in the GithubService class


@patch.object(Github, "__new__")
@patch.object(AIOHTTPTransport, "__new__")
@patch.object(Client, "__new__")
@patch.object(Constants, "__new__")
@patch.object(Organisation, "__new__")
class TestAmendUserRepositoryAccess(unittest.TestCase):

    def test_main_smoke_test(self, mock1, mock2, mock3, mock4, mock5):
        amend_user_repository_access.main()


if __name__ == "__main__":
    unittest.main()
