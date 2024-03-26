import os
import pandas as pd

from datetime import date, timedelta
from services.slack_service import SlackService
from config.constants import SR_SLACK_CHANNEL


def get_environment_variables() -> tuple:
    slack_token = os.getenv("ADMIN_SLACK_TOKEN")
    if not slack_token:
        raise ValueError(
            "The env variable ADMIN_SLACK_TOKEN is empty or missing")
    
    return slack_token

def str_yesterday():
    today = date.today()
    yesterday = today - timedelta(days=1)
    str_yesterday = str(yesterday)

    return str_yesterday

def yesterdays_support_requests_message():
    msg = (
        f"Good morning, \n\n"
        f"Yesterday we received {str_yday_total} Support Requests \n\n"
        f"Here's a breakdown of esterdays Support Requests: \n {yday_breakdown} \n"
    )

    return msg

def df():

    # Create dataframe from csv and set max rows
    df = pd.read_csv('csv/support_requests_mar24.csv')
    pd.options.display.max_rows = 9999

    # Set the index to Request Type column
    df.set_index(['Request Type'])

def str_yday_total():

    # Count requests in column that matches yesterdays date
    yday_total = df[str_yesterday].sum()
    str_yday_total = str(yday_total)

    return str_yday_total

def yday_breakdown():

    # Create mask to remove NaN fields from 'str_yesterday' and return Request Types and amount
    notna_msk = df[str_yesterday].notna()
    cols = ['Request Type', str_yesterday]
    yday_breakdown = df.loc[notna_msk, cols]

    return yday_breakdown

def main():

    slack_token = get_environment_variables()
    slack_service = SlackService(str(slack_token))

    slack_service.send_message_to_plaintext_channel_name(
        yesterdays_support_requests_message(), SR_SLACK_CHANNEL
    )

if __name__ == "__main__":
    main()