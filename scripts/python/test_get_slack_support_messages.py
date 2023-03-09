import unittest
from unittest.mock import MagicMock, patch

import get_slack_support_messages
# TODO: This mock needs fixing before tests can be implemented


@patch("slack_sdk.WebClient.__new__", new=MagicMock(conversations_history=MagicMock(has_more=False)))
@patch("os.environ", new=MagicMock(SLACK_BOT_TOKEN="token"))
class TestGetSlackSupportMessages(unittest.TestCase):

    # TODO: requires deeply nested mocking to smoke test due to infinite loop.
    def ignore_test_main_smoke_test(self):
        get_slack_support_messages.main()


if __name__ == "__main__":
    unittest.main()
