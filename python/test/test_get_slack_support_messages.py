import os
import unittest
from unittest.mock import patch

from python.scripts import get_slack_support_messages
from python.lib.moj_slack import MojSlack


@patch.object(MojSlack, "__new__")
class TestGetSlackSupportMessages(unittest.TestCase):

    @patch.dict(os.environ, {"SLACK_BOT_TOKEN": "token"})
    def test_main_smoke_test(self, moj_slack_mock):
        get_slack_support_messages.main()

    def test_main_returns_error_when_no_token_provided(self, moj_slack_mock):
        self.assertRaises(
            ValueError, get_slack_support_messages.main)


if __name__ == "__main__":
    unittest.main()
