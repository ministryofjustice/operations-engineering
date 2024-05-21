import sys
import unittest
from unittest.mock import patch, call
from bin import delete_cnames
from services.route_53_service import Route53Service


class TestDeleteCNames(unittest.TestCase):

    def test_main_returns_error_when_no_cli_arguments_provided(self):
        with patch.object(sys, 'argv', []):
            self.assertRaises(ValueError, delete_cnames.main)

    @patch.object(Route53Service, "delete_cname_records")
    def test_main_smoke_test(self, mock_delete_cname_records):
        with patch.object(sys, 'argv', ["id1", "id2"]):
            delete_cnames.main()
            mock_delete_cname_records.assert_has_calls([call("id1"), call("id2")])


if __name__ == "__main__":
    unittest.main()
