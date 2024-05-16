import os
from dataclasses import dataclass
from datetime import date, timedelta
from os.path import exists

import pandas as pd

from config.constants import SR_SLACK_CHANNEL
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
    

def create_dataframe_from_csv(filename:str):

    dataframe = pd.read_csv(filename)
    pd.options.display.max_rows = 9999

    dataframe.set_index('Type')

    return dataframe

    
def yesterdays_date():
    today = date.today()
    yesterday = today - timedelta(days=1)
    str_yesterday = str(yesterday)

    return str_yesterday


def get_environment_variables() -> tuple:
    slack_token = os.getenv("ADMIN_SLACK_TOKEN")
    if not slack_token:
        raise ValueError(
            "The env variable ADMIN_SLACK_TOKEN is empty or missing")

    return slack_token


def get_dict_of_requests_and_volume(requests: list[SupportRequest]) -> dict[SupportRequest, int]:
    dict_of_requests = {}
 
    for request in requests:
        dict_of_requests[request.request_action] += 1
    
    return dict_of_requests


def yesterdays_support_requests_message(yesterdays_support_requests: list[SupportRequest]):
    dict_of_requests_and_volume = get_dict_of_requests_and_volume(yesterdays_support_requests)
    
    msg = (
        f"Good morning, \n\n"
        f"Yesterday we received {len(yesterdays_support_requests)} Support Requests: \n\n"
    )
    yesterdays_support_requests = list(dict.fromkeys(yesterdays_support_requests))
    for request in yesterdays_support_requests:
        number_of_requests = dict_of_requests_and_volume[request.request_action]
        msg += f"--\n*Type:* {request.request_type}\n*Action:* {request.request_action}\n*Number of requests:* {number_of_requests}\n"
    
    return msg


def get_support_requests_from_csv(filepath:str) ->list[SupportRequest]:
    if exists(filepath):
        return get_list_of_support_requests(create_dataframe_from_csv(filepath))
    raise FileExistsError(
        f"File path {filepath} does not exist."
    )


def get_list_of_support_requests(data) -> list[SupportRequest]:
        list_of_support_requests = []
        for _, row in data.iterrows():
            list_of_support_requests.append(SupportRequest(row['Type'], row['Action'], row['Date']))
        
        return list_of_support_requests

            
def get_yesterdays_support_requests(all_support_requests: list[SupportRequest]) -> list[SupportRequest]:
    yesterday = yesterdays_date()
    list_of_yesterdays_support_requests = []
    for request in all_support_requests:
        if request.request_date == yesterday:
            list_of_yesterdays_support_requests.append(request)
        
    return list_of_yesterdays_support_requests


def main():

    slack_token = get_environment_variables()
    slack_service = SlackService(str(slack_token))
    FILE_PATH = 'data/support_stats/support_stats.csv'
    all_support_requests = get_support_requests_from_csv(FILE_PATH)
    yesterdays_requests = get_yesterdays_support_requests(all_support_requests)
    slack_message = yesterdays_support_requests_message(yesterdays_requests)

    slack_service.send_message_to_plaintext_channel_name(
        slack_message, SR_SLACK_CHANNEL
    )


if __name__ == "__main__":
    main()
