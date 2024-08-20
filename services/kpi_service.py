import logging
from typing import Dict

import requests
from requests import Response

logger = logging.getLogger("myapp")
logging.basicConfig()


class KpiService:
    def __init__(self, base_url: str, api_key: str):
        self.__base_url = base_url
        self.__request_headers = {"X-API-KEY": api_key, "Content-Type": "application/json"}
        self.__request_timeout = 10

    def __post(self, endpoint: str, data: Dict) -> Response:
        return requests.post(url=f"{self.__base_url}{endpoint}", headers=self.__request_headers, timeout=self.__request_timeout, json=data)

    def track_number_of_repositories_with_standards_label(self, count: int):
        self.__post("/api/indicator/add", {"indicator": "REPOSITORIES_WITH_STANDARDS_LABEL", "count": count})

    def track_enterprise_github_actions_quota_usage(self, count: int):
        self.__post("/api/indicator/add", {"indicator": "ENTERPRISE_GITHUB_ACTIONS_QUOTA_USAGE", "count": count})
