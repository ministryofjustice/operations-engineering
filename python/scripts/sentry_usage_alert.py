import os

from python.clients.sentry_client import SentryClient
from python.config.logging_config import logging
from python.services.sentry_service import SentryService


def get_environment_variables() -> str:
    sentry_token = os.getenv("SENTRY_TOKEN")
    if not sentry_token:
        raise ValueError("The env variable SENTRY_TOKEN is empty or missing")

    return sentry_token


def main():
    sentry_token = get_environment_variables()
    period_in_days = 1
    sentry_service = SentryService(
        SentryClient("https://sentry.io", sentry_token))
    error_usage_stats, transaction_usage_stats = sentry_service.get_quota_usage_for_period_in_days(
        period_in_days)

    logging.info(
        f"Error quota consumed over past {period_in_days} days [ {error_usage_stats.total} / {error_usage_stats.max_usage} ]. Percentage consumed: [ {error_usage_stats.percentage_of_quota_used:.2%} ]")
    logging.info(
        f"Transaction quota consumed over past {period_in_days} days [ {transaction_usage_stats.total} / {transaction_usage_stats.max_usage} ]. Percentage consumed: [ {transaction_usage_stats.percentage_of_quota_used:.2%} ]")


if __name__ == "__main__":
    main()
