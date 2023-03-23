import os
import unittest
from unittest.mock import MagicMock, patch

from python.scripts import delete_cnames


@patch("boto3.client", new=MagicMock)
@patch("botocore.client.BaseClient.__new__", new=MagicMock)
class TestDeleteCNames(unittest.TestCase):

    @patch.dict(os.environ, {"HOSTED_ZONE_1": "123"})
    @patch.dict(os.environ, {"HOSTED_ZONE_2": "123"})
    def test_main_smoke_test(self):
        delete_cnames.main()

    @patch.dict(os.environ, {"HOSTED_ZONE_2": "123"})
    def test_main_returns_error_when_first_token_is_not_provided(self):
        self.assertRaises(
            ValueError, delete_cnames.main)

    @patch.dict(os.environ, {"HOSTED_ZONE_1": "123"})
    def test_main_returns_error_when_second_token_is_not_provided(self):
        self.assertRaises(
            ValueError, delete_cnames.main)


if __name__ == "__main__":
    unittest.main()
