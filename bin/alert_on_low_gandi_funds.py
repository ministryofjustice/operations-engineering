import os
import sys
from services.gandi_service import GandiService
from services.slack_service import SlackService
from config.constants import SLACK_CHANNEL

GANDI_FUND_THRESHOLD = 5000


def low_gandi_funds_message(remaining_gandi_funds):
    msg = (
        f"Hi all, \n\n"
        f"This is an alert do inform you that Gandi funds are low. \n\n"
        f"*We currently have £{remaining_gandi_funds} left out of £{GANDI_FUND_THRESHOLD}*\n"
        f"Please seek to add more funds to the account as soon as possible.\n\n"
        f"Have a swell day, \n\n"
        "The GitHub Organisation Monitoring Bot"
    )

    return msg


def send_gandi_alert_to_slack(remaining_gandi_funds):
    print(f'Sending alert to slack as funds are low: {remaining_gandi_funds}')


def alert_on_low_gandi_funds():
    gandi_token = os.environ.get("GANDI_FUNDS_TOKEN")
    if gandi_token is None:
        print("No GANDI_FUNDS_TOKEN environment variable set")
        sys.exit(1)
    slack_token = os.environ.get("ADMIN_SLACK_TOKEN")
    if slack_token is None:
        print("No SLACK_TOKEN environment variable set")
        sys.exit(1)
    organisation_id = os.environ.get("GANDI_ORG_ID")
    gandi_service = GandiService(gandi_token, "v5/billing/info/")

    remaining_gandi_funds = gandi_service.get_current_account_balance_from_org(organisation_id)

    if remaining_gandi_funds < GANDI_FUND_THRESHOLD:
        SlackService(slack_token).send_message_to_plaintext_channel_name(
            low_gandi_funds_message(remaining_gandi_funds), SLACK_CHANNEL)


if __name__ == "__main__":
    alert_on_low_gandi_funds()
