from textwrap import dedent
from slack_sdk import WebClient


class SlackService:
    OPERATIONS_ENGINEERING_ALERTS_CHANNEL_ID = "C033QBE511V"
    DATE_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

    # Added to stop TypeError on instantiation. See https://github.com/python/cpython/blob/d2340ef25721b6a72d45d4508c672c4be38c67d3/Objects/typeobject.c#L4444
    def __new__(cls, *_, **__):
        return super(SlackService, cls).__new__(cls)

    def __init__(self, slack_token: str) -> None:
        self.slack_client = WebClient(slack_token)

    def send_alert_to_operations_engineering(self, message: str):
        self.slack_client.chat_postMessage(channel=self.OPERATIONS_ENGINEERING_ALERTS_CHANNEL_ID,
                                           mrkdown=True,
                                           blocks=[
                                               {
                                                   "type": "section",
                                                   "text": {
                                                       "type": "mrkdwn",
                                                       "text": dedent(f"""{message}""").strip("\n")
                                                   }
                                               }
                                           ]
                                           )
