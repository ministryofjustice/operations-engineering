import os
from dataclasses import dataclass
from datetime import date, timedelta
from os.path import exists

import pandas as pd
from collections import defaultdict

from services.slack_service import SlackService


@dataclass
class SupportRequest:
    request_type: str
    request_action: str
    request_date: str

    def __init__(self, request_type: str, request_action: str, request_date: str):
        self.request_type = request_type
        self.request_action = request_action
        self.request_date = request_date

    def __hash__(self):
        return hash(self.request_action)


def create_dataframe_from_csv(filename: str):

    dataframe = pd.read_csv(filename)
    pd.options.display.max_rows = 9999

    dataframe.set_index("Type")

    return dataframe


def get_previous_working_day(date_today):
    diff = 1
    if date_today.weekday() == 0:
        diff = 3
    else:
        diff = 1

    last_working_day = date_today - timedelta(days=diff)
    str_last_working_day = str(last_working_day)

    return str_last_working_day


def get_environment_variables() -> tuple:
    slack_token = os.getenv("ADMIN_SLACK_TOKEN")
    if not slack_token:
        raise ValueError("The env variable ADMIN_SLACK_TOKEN is empty or missing")

    return slack_token


def get_dict_of_requests_and_volume(
    requests: list[SupportRequest],
) -> dict[SupportRequest, int]:
    dict_of_requests = defaultdict(int)

    for request in requests:
        dict_of_requests[request.request_action] += 1

    return dict_of_requests


def craft_support_statistics(
    yesterdays_support_requests: list[SupportRequest], date_today=date.today()
):
    dict_of_requests_and_volume = get_dict_of_requests_and_volume(
        yesterdays_support_requests
    )

    previous_support_day = get_previous_working_day(date_today)

    msg = f"On {previous_support_day} we received {len(yesterdays_support_requests)} Support Requests: \n\n"
    yesterdays_support_requests = list(dict.fromkeys(yesterdays_support_requests))
    for request in yesterdays_support_requests:
        number_of_requests = dict_of_requests_and_volume[request.request_action]
        msg += f"--\n*Type:* {request.request_type}\n*Action:* {request.request_action}\n*Number of requests:* {number_of_requests}\n"

    return msg


def get_support_requests_from_csv(filepath: str) -> list[SupportRequest]:
    if exists(filepath):
        return get_list_of_support_requests(create_dataframe_from_csv(filepath))
    raise FileExistsError(f"File path {filepath} does not exist.")


def get_list_of_support_requests(data) -> list[SupportRequest]:
    list_of_support_requests = []
    for _, row in data.iterrows():
        list_of_support_requests.append(
            SupportRequest(row["Type"], row["Action"], row["Date"])
        )

    return list_of_support_requests


def get_yesterdays_support_requests(
    all_support_requests: list[SupportRequest], todays_date
) -> list[SupportRequest]:
    yesterday = get_previous_working_day(todays_date)  # yesterdays_date()
    list_of_yesterdays_support_requests = []
    for request in all_support_requests:
        if request.request_date == yesterday:
            list_of_yesterdays_support_requests.append(request)

    return list_of_yesterdays_support_requests


def main(todays_date=date.today(), file_path="data/support_stats/support_stats.csv"):
    slack_token = get_environment_variables()
    slack_service = SlackService(str(slack_token))
    all_support_requests = get_support_requests_from_csv(file_path)
    yesterdays_requests = get_yesterdays_support_requests(
        all_support_requests, todays_date
    )
    support_statistics = craft_support_statistics(yesterdays_requests, todays_date)

    slack_service.send_slack_support_stats_report(support_statistics)


if __name__ == "__main__":
    main()
