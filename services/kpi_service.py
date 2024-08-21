import logging
from typing import Dict

import requests
from requests import Response

logger = logging.getLogger("myapp")
logging.basicConfig()


class KpiService:
    # Added to stop TypeError on instantiation. See https://github.com/python/cpython/blob/d2340ef25721b6a72d45d4508c672c4be38c67d3/Objects/typeobject.c#L4444
    def __new__(cls, *args, **kwargs):
        return super(KpiService, cls).__new__(cls)

    def __init__(self, base_url: str, api_key: str):
        self.__base_url = base_url
        self.__request_headers = {
            "X-API-KEY": api_key,
            "Content-Type": "application/json",
        }
        self.__request_timeout = 10

    def __post(self, endpoint: str, data: Dict) -> Response:
        return requests.post(
            url=f"{self.__base_url}{endpoint}",
            headers=self.__request_headers,
            timeout=self.__request_timeout,
            json=data,
        )

    def __add_indicator(self, indicator: str, count: int) -> None:
        self.__post("/api/indicator/add", {"indicator": indicator, "count": count})

    def track_number_of_repositories_with_standards_label(self, count: int) -> None:
        self.__add_indicator("REPOSITORIES_WITH_STANDARDS_LABEL", count)

    def track_sentry_transactions_used_for_day(self, count: int):
        self.__add_indicator("SENTRY_TRANSACTIONS_USED_OVER_PAST_DAY", count)

    def track_sentry_errors_used_for_day(self, count: int):
        self.__add_indicator("SENTRY_ERRORS_USED_OVER_PAST_DAY", count)

    def track_sentry_replays_used_for_day(self, count: int):
        self.__add_indicator("SENTRY_REPLAYS_USED_OVER_PAST_DAY", count)
