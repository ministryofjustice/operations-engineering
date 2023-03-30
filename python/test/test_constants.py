import os
import unittest
from unittest.mock import patch

from python.lib.constants import Constants


@patch.dict(os.environ, {"ORG_NAME": "orgname"})
@patch.dict(os.environ, {"ADMIN_GITHUB_TOKEN": "token"})
class TestConstants(unittest.TestCase):

    def test_create_object(self):
        constants = Constants()


if __name__ == "__main__":
    unittest.main()
