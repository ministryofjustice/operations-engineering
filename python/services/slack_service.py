from slack_sdk import WebClient

from python.services.sentry_service import UsageStats


class SlackService:
    OPERATIONS_ENGINEERING_ALERTS_CHANNEL_ID = "C033QBE511V"

    def __init__(self, slack_token: str) -> None:
        self.slack_client = WebClient(slack_token)

    def send_error_usage_alert_to_operations_engineering(self, period_in_days: int, usage_stats: UsageStats,
                                                         usage_threshold: float):
        self.slack_client.chat_postMessage(channel=self.OPERATIONS_ENGINEERING_ALERTS_CHANNEL_ID,
                                           mrkdown=True,
                                           text=f"*Sentry Errors have exceeded {usage_threshold:.2%} usage in the past {period_in_days} days*\n`This is a test message for Sentry Error alerts!` :test_tube:\nError quota consumed over past {period_in_days} days [ {usage_stats.total} / {usage_stats.max_usage} ]\nPercentage consumed: [ {usage_stats.percentage_of_quota_used:.2%} ]")

    def send_transaction_usage_alert_to_operations_engineering(self, period_in_days: int, usage_stats: UsageStats,
                                                               usage_threshold: float):
        self.slack_client.chat_postMessage(channel=self.OPERATIONS_ENGINEERING_ALERTS_CHANNEL_ID,
                                           mrkdown=True,
                                           text=f"*Sentry Transactions have exceeded {usage_threshold:.2%} usage in the past {period_in_days} days*\n`This is a test message for Sentry Transactions alerts!` :test_tube:\nTransaction quota consumed over past {period_in_days} days [ {usage_stats.total} / {usage_stats.max_usage} ]\nPercentage consumed: [ {usage_stats.percentage_of_quota_used:.2%} ]")
