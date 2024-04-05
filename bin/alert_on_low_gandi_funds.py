import os
from services.gandi_service import GandiService

GANDI_FUND_THRESHOLD = 500


def send_gandi_alert_to_slack(remaining_gandi_funds):
    print(f'Sending alert to slack as funds are low: {remaining_gandi_funds}')


def alert_on_low_gandi_funds():
    gandi_token = os.environ.get("GANDI_FUNDS_TOKEN")
    organisation_id = os.environ.get("GANDI_ORG_ID")
    gandi_service = GandiService(gandi_token, "v5/billing/info/")

    remaining_gandi_funds = gandi_service.get_current_account_balance_from_org(organisation_id)

    if remaining_gandi_funds < GANDI_FUND_THRESHOLD:
        send_gandi_alert_to_slack(remaining_gandi_funds)


if __name__ == "__main__":
    alert_on_low_gandi_funds()
