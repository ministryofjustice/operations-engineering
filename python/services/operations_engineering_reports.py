import json

import requests


class OperationsEngineeringReportsService:
    """Communicate with the operations-engineering-reports API. This service is used to send reports
    to the API, which will then be displayed on the reports page.

    Arguments:
        url {str} -- The url of the operations-engineering-reports API.
        endpoint {str} -- The endpoint of the operations-engineering-reports API.
        api_key {str} -- The API key to use for the operations-engineering-reports API.
        enc_key {hex} -- The encryption key to use for the operations-engineering-reports API.

    """

    def __init__(self, url: str, endpoint: str, api_key: str) -> None:
        self.__reports_url = url
        self.__endpoint = endpoint
        self.__api_key = api_key

    def override_repository_standards_reports(self, reports: list[dict]) -> None:
        """Send a list of GitHubRepositoryStandardsReport objects represented as json objects
        to the operations-engineering-reports API endpoint. This will overwrite any existing
        reports for the given repositories.

        Arguments:
            reports {list[dict]} -- A list of GitHubRepositoryStandardsReport objects represented
            as json objects.

        Raises:
            Exception: If the status code of the POST request is not 200.

        """
        status = self.__http_post(reports)
        if status != 200:
            raise AssertionError(
                f"Received status code {status} from {self.__reports_url}/{self.__endpoint}")

    def __http_post(self, data: list[dict]) -> int:
        headers = {
            "Content-Type": "application/json",
            "X-API-KEY": self.__api_key,
            "User-Agent": "reports-service-layer",
        }

        url = f"{self.__reports_url}/{self.__endpoint}"

        return requests.post(url, headers=headers, json=data, timeout=3).status_code
