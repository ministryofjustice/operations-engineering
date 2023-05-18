import json
import sys

import requests
from cryptography.fernet import Fernet

from python.services.repository_standards_service import GitHubRepositoryStandardsReport


class ReportsService:
    """
    This class is used to communicate with the operations-engineering-reports API.
    """

    def __init__(self, url: str, endpoint: str, api_key: str, enc_key: hex) -> None:
        self.reports_url = url
        self.endpoint = endpoint
        self.api_key = api_key
        self.encryption_key = enc_key

    def override_repository_standards_reports(self, reports: list[GitHubRepositoryStandardsReport]) -> None:
        """
        Send the report to the operations-engineering-reports API.
        All data is encrypted before sending, using an asymmetric key generated beforehand.
        """
        data = self.__encrypt(reports)

        self.__http_post(data)

    def __http_post(self, data) -> None:
        headers = {
            "Content-Type": "application/json",
            "X-API-KEY": self.api_key,
            "User-Agent": "reports-service-layer",
        }

        url = self.reports_url+self.endpoint

        requests.post(url, headers=headers,
                            json=data, timeout=3)

    def __encrypt(self, payload: any):
        key = bytes.fromhex(self.encryption_key)
        fernet = Fernet(key)

        json_data = json.dumps(payload.to_json())
        sys.exit()
        encrypted_data_as_bytes = fernet.encrypt(
            json_data.__str__().encode())
        encrypted_data_bytes_as_string = encrypted_data_as_bytes.decode()

        return encrypted_data_bytes_as_string


