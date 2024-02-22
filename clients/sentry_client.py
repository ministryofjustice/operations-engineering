from datetime import datetime

import requests
from requests import Response


class SentryClient:
    # Added to stop TypeError on instantiation. See https://github.com/python/cpython/blob/d2340ef25721b6a72d45d4508c672c4be38c67d3/Objects/typeobject.c#L4444
    def __new__(cls, *_, **__):
        return super(SentryClient, cls).__new__(cls)

    def __init__(self, base_url: str, token: str) -> None:
        self.__base_url = base_url
        self.__request_headers = {"Authorization": f"Bearer {token}"}
        self.__request_timeout = 10

    def __get(self, endpoint: str) -> Response:
        return requests.get(f"{self.__base_url}{endpoint}", headers=self.__request_headers,
                            timeout=self.__request_timeout)

    def get_usage_total_for_period_in_days(self, category: str, period_in_days: int) -> tuple[int, datetime, datetime]:
        json_data = self.__get(
            f"/api/0/organizations/ministryofjustice/stats_v2/?statsPeriod={period_in_days}d&field=sum(quantity)&category={category}&outcome=accepted"
        ).json()
        total = json_data["groups"][0]["totals"]["sum(quantity)"]
        start_time = datetime.strptime(
            json_data["start"], "%Y-%m-%dT%H:%M:%SZ")
        end_time = datetime.strptime(json_data["end"], "%Y-%m-%dT%H:%M:%SZ")
        return total, start_time, end_time
