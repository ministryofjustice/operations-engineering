import os

from python.clients.sentry_client import SentryClient
from python.config.logging_config import logging


def get_environment_variables() -> str:
    sentry_token = os.getenv("SENTRY_TOKEN")
    if not sentry_token:
        raise ValueError("The env variable SENTRY_TOKEN is empty or missing")

    return sentry_token


def main():
    sentry_token = get_environment_variables()
    sentry_client = SentryClient("https://sentry.io", sentry_token)
    logging.info(sentry_client.get_organization_stats_for_one_day())


if __name__ == "__main__":
    main()
