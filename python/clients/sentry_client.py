from typing import Any

import requests
from requests import Response


class SentryClient:
    def __init__(self, base_url: str, token: str):
        self.__base_url = base_url
        self.__request_headers = {"Authorization": f"Bearer {token}"}
        self.__request_timeout = 10

    def __get(self, endpoint: str) -> Response:
        return requests.get(f"{self.__base_url}{endpoint}", headers=self.__request_headers,
                            timeout=self.__request_timeout)

    def get_organization_stats_for_one_day(self) -> Any:
        return self.__get(
            "/api/0/organizations/ministryofjustice/stats_v2/?statsPeriod=1d&field=sum(quantity)&groupBy=category").json()
