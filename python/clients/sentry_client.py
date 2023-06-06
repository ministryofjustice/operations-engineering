from typing import Any

import requests
from requests import Response


class SentryClient:
    def __init__(self, base_url: str, token: str) -> None:
        self.__base_url = base_url
        self.__request_headers = {"Authorization": f"Bearer {token}"}
        self.__request_timeout = 10

    def __get(self, endpoint: str) -> Response:
        return requests.get(f"{self.__base_url}{endpoint}", headers=self.__request_headers,
                            timeout=self.__request_timeout)

    def get_usage_total_for_period_in_days(self, category: str, period_in_days: int) -> Any:
        json_data = self.__get(
            f"/api/0/organizations/ministryofjustice/stats_v2/?statsPeriod={period_in_days}d&field=sum(quantity)&category={category}&outcome=accepted").json()
        return json_data["groups"][0]['totals']['sum(quantity)']
