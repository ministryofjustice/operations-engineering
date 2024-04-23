from dataclasses import dataclass
from datetime import datetime

from clients.sentry_client import SentryClient


@dataclass
class UsageStats:
    total: int
    max_usage: int
    percentage_of_quota_used: float
    start_time: datetime
    end_time: datetime


class SentryService:
    MONTHLY_ERROR_QUOTA = 4000000
    DAILY_ERROR_QUOTA = int(MONTHLY_ERROR_QUOTA / 31)
    MONTHLY_TRANSACTION_QUOTA = 30000000
    DAILY_TRANSACTION_QUOTA = int(MONTHLY_TRANSACTION_QUOTA / 31)
    MONTHLY_REPLAY_QUOTA = 800000
    DAILY_REPLAY_QUOTA = int(MONTHLY_REPLAY_QUOTA / 31)

    def __init__(self, sentry_client: SentryClient):
        self.sentry_client = sentry_client

    def __get_max_usage_for_period_in_days(self, period_in_days: int) -> tuple[int, int, int]:
        max_error_usage_for_period = self.DAILY_ERROR_QUOTA * period_in_days
        max_transaction_usage_for_period = self.DAILY_TRANSACTION_QUOTA * period_in_days
        max_replay_usage_for_period = self.DAILY_REPLAY_QUOTA * period_in_days

        return max_error_usage_for_period, max_transaction_usage_for_period, max_replay_usage_for_period

    def get_quota_usage_for_period_in_days(self, period_in_days: int) -> tuple[UsageStats, UsageStats, UsageStats]:
        error_total, error_start_time, error_end_time = self.sentry_client.get_usage_total_for_period_in_days(
            "error", period_in_days)
        transaction_total, transaction_start_time, transaction_end_time = self.sentry_client.get_usage_total_for_period_in_days(
            "transaction", period_in_days)
        replay_total, replay_start_time, replay_end_time = self.sentry_client.get_usage_total_for_period_in_days(
            "replay", period_in_days)

        max_error_usage, max_transaction_usage, max_replay_usage = self.__get_max_usage_for_period_in_days(
            period_in_days)
        percentage_of_error_quota_used = error_total / max_error_usage
        percentage_of_transaction_quota_used = transaction_total / max_transaction_usage
        percentage_of_replay_quota_used = replay_total / max_replay_usage

        error_usage_stats = UsageStats(
            error_total,
            max_error_usage,
            percentage_of_error_quota_used,
            error_start_time,
            error_end_time
        )
        transaction_usage_stats = UsageStats(
            transaction_total, max_transaction_usage,
            percentage_of_transaction_quota_used,
            transaction_start_time,
            transaction_end_time
        )
        replay_usage_stats = UsageStats(
            replay_total,
            max_replay_usage,
            percentage_of_replay_quota_used,
            replay_start_time,
            replay_end_time
        )

        return error_usage_stats, transaction_usage_stats, replay_usage_stats
