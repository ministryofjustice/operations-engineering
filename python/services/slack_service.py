from textwrap import dedent
from urllib.parse import quote

from slack_sdk import WebClient

from python.services.sentry_service import UsageStats


class SlackService:
    OPERATIONS_ENGINEERING_ALERTS_CHANNEL_ID = "C033QBE511V"
    DATE_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

    # Added to stop TypeError on instantiation. See https://github.com/python/cpython/blob/d2340ef25721b6a72d45d4508c672c4be38c67d3/Objects/typeobject.c#L4444
    def __new__(cls, *_, **__):
        return super(SlackService, cls).__new__(cls)

    def __init__(self, slack_token: str) -> None:
        self.slack_client = WebClient(slack_token)

    def send_error_usage_alert_to_operations_engineering(self, period_in_days: int, usage_stats: UsageStats,
                                                         usage_threshold: float):
        self.slack_client.chat_postMessage(channel=self.OPERATIONS_ENGINEERING_ALERTS_CHANNEL_ID,
                                           mrkdown=True,
                                           blocks=[
                                               {
                                                   "type": "section",
                                                   "text": {
                                                       "type": "mrkdwn",
                                                       "text": dedent(f"""
                                                           :warning: *Sentry Errors Usage Alert :sentry::warning:*
                                                           - Usage threshold: {usage_threshold:.0%}
                                                           - Period: {period_in_days} {'days' if period_in_days > 1 else 'day'}
                                                           - Max usage for period: {usage_stats.max_usage} Errors
                                                           - Errors consumed over period: {usage_stats.total}
                                                           - Percentage consumed: {usage_stats.percentage_of_quota_used:.0%}
                                                       """).strip("\n")
                                                   }
                                               },
                                               {
                                                   "type": "divider"
                                               },
                                               {
                                                   "type": "section",
                                                   "text": {
                                                       "type": "mrkdwn",
                                                       "text": " Check Sentry for projects reporting excessive errors :eyes:"
                                                   },
                                                   "accessory": {
                                                       "type": "button",
                                                       "text": {
                                                           "type": "plain_text",
                                                           "text": ":sentry: Error usage for period",
                                                           "emoji": True
                                                       },
                                                       "url": f"https://ministryofjustice.sentry.io/stats/?dataCategory=errors&end={quote(usage_stats.end_time.strftime(self.DATE_FORMAT))}&sort=-accepted&start={quote(usage_stats.start_time.strftime(self.DATE_FORMAT))}&utc=true"
                                                   }
                                               }
                                           ])

    def send_transaction_usage_alert_to_operations_engineering(self, period_in_days: int, usage_stats: UsageStats,
                                                               usage_threshold: float):
        self.slack_client.chat_postMessage(channel=self.OPERATIONS_ENGINEERING_ALERTS_CHANNEL_ID,
                                           mrkdown=True,
                                           blocks=[
                                               {
                                                   "type": "section",
                                                   "text": {
                                                       "type": "mrkdwn",
                                                       "text": dedent(f"""
                                                           :sentry: *Sentry Transactions Usage Alert :warning:*
                                                           - Usage threshold: {usage_threshold:.0%}
                                                           - Period: {period_in_days} {'days' if period_in_days > 1 else 'day'}
                                                           - Max usage for period: {usage_stats.max_usage} Transactions
                                                           - Transactions consumed over period: {usage_stats.total}
                                                           - Percentage consumed: {usage_stats.percentage_of_quota_used:.0%}
                                                       """).strip("\n")
                                                   }
                                               },
                                               {
                                                   "type": "divider"
                                               },
                                               {
                                                   "type": "section",
                                                   "text": {
                                                       "type": "mrkdwn",
                                                       "text": " Check Sentry for projects consuming excessive transactions :eyes:"
                                                   },
                                                   "accessory": {
                                                       "type": "button",
                                                       "text": {
                                                           "type": "plain_text",
                                                           "text": ":sentry: Transaction usage for period",
                                                           "emoji": True
                                                       },
                                                       "url": f"https://ministryofjustice.sentry.io/stats/?dataCategory=transactions&end={quote(usage_stats.end_time.strftime(self.DATE_FORMAT))}&sort=-accepted&start={quote(usage_stats.start_time.strftime(self.DATE_FORMAT))}&utc=true"
                                                   }
                                               }
                                           ])
