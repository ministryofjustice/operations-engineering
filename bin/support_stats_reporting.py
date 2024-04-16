import os
from datetime import date, timedelta
import pandas as pd

from services.slack_service import SlackService
from config.constants import SR_SLACK_CHANNEL


def create_dataframe():

    # Create dataframe from csv and set max rows
    dataframe = pd.read_csv('csv/data-all.csv')
    pd.options.display.max_rows = 9999

    # Set the index to Request Type column
    dataframe.set_index(['Request Type'])

    return dataframe


def yesterdays_date():
    today = date.today()
    yesterday = today - timedelta(days=1)
    str_yesterday = str(yesterday)

    return str_yesterday


def yesterdays_requests_total(yesterdays_date):

    yesterdays_requests = create_dataframe[yesterdays_date].sum()

    return yesterdays_requests


def yesterdays_requests_breakdown(yesterdays_date):

    # Create mask to remove NaN fields from 'str_yesterday' and return Request Types and amount
    notna_msk = create_dataframe[yesterdays_date].notna()
    cols = ['Request Type', yesterdays_date]
    yesterdays_breakdown = create_dataframe.loc[notna_msk, cols]

    return yesterdays_breakdown


def get_environment_variables() -> tuple:
    slack_token = os.getenv("ADMIN_SLACK_TOKEN")
    if not slack_token:
        raise ValueError(
            "The env variable ADMIN_SLACK_TOKEN is empty or missing")

    return slack_token


def yesterdays_support_requests_message(yesterdays_requests_total, yesterdays_requests_breakdown):
    msg = (
        f"Good morning, \n\n"
        f"Yesterday we received {yesterdays_requests_total} Support Requests \n\n"
        f"Here's a breakdown of yesterdays Support Requests: \n {yesterdays_requests_breakdown} \n"
    )

    return msg


def main():

    slack_token = get_environment_variables()
    slack_service = SlackService(str(slack_token))
    yesterdays_date = yesterdays_date()

    slack_message = yesterdays_support_requests_message(yesterdays_requests_total(yesterdays_date), yesterdays_requests_breakdown(yesterdays_date))

    slack_service.send_message_to_plaintext_channel_name(
        slack_message, SR_SLACK_CHANNEL
    )


if __name__ == "__main__":
    main()
