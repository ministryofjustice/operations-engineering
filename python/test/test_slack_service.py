import unittest
from unittest.mock import MagicMock, patch

from python.services.slack_service import SlackService


@patch("slack_sdk.WebClient.__new__")
class TestSendAlertToOperationsEngineering(unittest.TestCase):

    # pylint: disable=R6301
    def test_downstream_services_called(self, mock_slack_client: MagicMock):
        message = "*some*\nmessage"
        SlackService(
            "").send_alert_to_operations_engineering(message)
        mock_slack_client.return_value.chat_postMessage.assert_called_with(
            channel="C033QBE511V",
            mrkdown=True,
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*some*\nmessage"
                    }
                }
            ]
        )


if __name__ == "__main__":
    unittest.main()
