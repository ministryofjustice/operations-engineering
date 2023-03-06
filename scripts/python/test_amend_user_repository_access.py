import unittest
from unittest.mock import patch

from github import Github
from gql import Client
from gql.transport.aiohttp import AIOHTTPTransport

import amend_user_repository_access


@patch.object(Github, "__new__")
@patch.object(AIOHTTPTransport, "__new__")
@patch.object(Client, "__new__")
class TestAmendUserRepositoryAccess(unittest.TestCase):

    def test_main_returns_error_when_no_token_provided(self, mock1, mock2, mock3):
        self.assertRaises(ValueError, amend_user_repository_access.main)


if __name__ == "__main__":
    unittest.main()
