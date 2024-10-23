import os
import sys
from services.gandi_service import GandiService
from services.slack_service import SlackService
from config.constants import GANDI_FUND_THRESHOLD


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
    if organisation_id is None:
        print("No GANDI_ORG_ID environment variable set")
        sys.exit(1)
    gandi_service = GandiService(gandi_token, "v5/billing/info/")

    remaining_gandi_funds = gandi_service.get_current_account_balance_from_org(organisation_id)

    if remaining_gandi_funds < GANDI_FUND_THRESHOLD:
        SlackService(slack_token).send_low_gandi_funds_alert(remaining_gandi_funds, GANDI_FUND_THRESHOLD)


if __name__ == "__main__":
    alert_on_low_gandi_funds()
