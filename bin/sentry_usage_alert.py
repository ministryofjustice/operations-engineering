import os

from clients.sentry_client import SentryClient
from config.logging_config import logging
from services.sentry_service import SentryService
from services.slack_service import SlackService


def get_environment_variables() -> tuple[str, str, int, float]:
    sentry_token = os.getenv("SENTRY_TOKEN")
    if not sentry_token:
        raise ValueError("The env variable SENTRY_TOKEN is empty or missing")

    slack_token = os.getenv("SLACK_TOKEN")
    if not slack_token:
        raise ValueError("The env variable SLACK_TOKEN is empty or missing")

    period_in_days = os.getenv("PERIOD_IN_DAYS") or 1
    usage_threshold = os.getenv("USAGE_THRESHOLD") or 60

    return sentry_token, slack_token, int(period_in_days), round(int(usage_threshold) / 100, 2)


def main():
    sentry_token, slack_token, period_in_days, usage_threshold = get_environment_variables()

    sentry_service = SentryService(
        SentryClient("https://sentry.io", sentry_token))
    slack_service = SlackService(slack_token)

    error_usage_stats, transaction_usage_stats = sentry_service.get_quota_usage_for_period_in_days(
        period_in_days)

    logging.info(
        f"Error quota consumed over past {period_in_days} {'days' if period_in_days > 1 else 'day'} [ {error_usage_stats.total} / {error_usage_stats.max_usage} ]. Percentage consumed over period: [ {error_usage_stats.percentage_of_quota_used:.0%} ]")
    logging.info(
        f"Transaction quota consumed over past {period_in_days} {'days' if period_in_days > 1 else 'day'} [ {transaction_usage_stats.total} / {transaction_usage_stats.max_usage} ]. Percentage consumed over period: [ {transaction_usage_stats.percentage_of_quota_used:.0%} ]")

    if error_usage_stats.percentage_of_quota_used > usage_threshold:
        slack_service.send_error_usage_alert_to_operations_engineering(period_in_days, error_usage_stats,
                                                                       usage_threshold)
    if transaction_usage_stats.percentage_of_quota_used > usage_threshold:
        slack_service.send_transaction_usage_alert_to_operations_engineering(period_in_days, transaction_usage_stats,
                                                                             usage_threshold)


if __name__ == "__main__":
    main()
