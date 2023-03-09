import unittest
from unittest.mock import MagicMock, patch

import delete_cnames


@patch("boto3.client", new=MagicMock)
@patch("botocore.client.BaseClient.__new__", new=MagicMock)
class TestDeleteCNames(unittest.TestCase):

    @patch("sys.argv", ["", "test"])
    def test_main_smoke_test(self):
        delete_cnames.main()


if __name__ == "__main__":
    unittest.main()
