from dataclasses import dataclass

from python.clients.sentry_client import SentryClient


@dataclass
class UsageStats:
    total: int
    max_usage: int
    percentage_of_quota_used: float


class SentryService:
    MONTHLY_ERROR_QUOTA = 4000000
    DAILY_ERROR_QUOTA = int(MONTHLY_ERROR_QUOTA / 31)
    MONTHLY_TRANSACTION_QUOTA = 30000000
    DAILY_TRANSACTION_QUOTA = int(MONTHLY_TRANSACTION_QUOTA / 31)

    def __init__(self, sentry_client: SentryClient):
        self.sentry_client = sentry_client

    def __get_max_usage_for_period_in_days(self, period_in_days: int) -> tuple[int, int]:
        max_error_usage_for_period = self.DAILY_ERROR_QUOTA * period_in_days
        max_transaction_usage_for_period = self.DAILY_TRANSACTION_QUOTA * period_in_days

        return max_error_usage_for_period, max_transaction_usage_for_period

    def get_quota_usage_for_period_in_days(self, period_in_days: int) -> tuple[UsageStats, UsageStats]:
        error_total = self.sentry_client.get_usage_total_for_period_in_days(
            "error", period_in_days)
        transaction_total = self.sentry_client.get_usage_total_for_period_in_days(
            "transaction", period_in_days)

        max_error_usage, max_transaction_usage = self.__get_max_usage_for_period_in_days(
            period_in_days)
        percentage_of_error_quota_used = error_total / max_error_usage
        percentage_of_transaction_quota_used = transaction_total / max_transaction_usage

        error_usage_stats = UsageStats(
            error_total, max_error_usage, percentage_of_error_quota_used)
        transaction_usage_stats = UsageStats(transaction_total, max_transaction_usage,
                                             percentage_of_transaction_quota_used)

        return error_usage_stats, transaction_usage_stats
