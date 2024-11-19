import logging
import requests

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# flake8: noqa

class OperationsEngineeringReportsService:
    """Communicate with the operations-engineering-reports API. This service is used to send reports
    to the API, which will then be displayed on the reports page.

    Arguments:
        url {str} -- The url of the operations-engineering-reports API.
        endpoint {str} -- The endpoint of the operations-engineering-reports API.
        api_key {str} -- The API key to use for the operations-engineering-reports API.

    """

    def __init__(self, url: str, endpoint: str, api_key: str, log_level="INFO") -> None:
        self.__reports_url = url
        self.__endpoint = endpoint
        self.__api_key = api_key

        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(log_level)
        self.logger.info(
            "Initialised %s with url: %s, endpoint: %s", self.__class__.__name__, self.__reports_url, self.__endpoint
        )

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
        #  Batched into groups of 10 due to database limitations
        self.logger.info("Sending %s repository standards reports to API.", len(reports))
        for i in range(0, len(reports), 10):
            chunk = reports[i: i + 10]
            status = self.__http_post(chunk)
            if status != 200:
                self.logger.error("Failed to send chunk starting from index %s. Received status: %s", i, status)
                raise ValueError(f"Failed to send repository standards reports to API. Received: {status}")
            self.logger.debug("Successfully sent chunk starting from index %s", i)

    def __http_post(self, data: list[dict]) -> int:
        headers = {
            "Content-Type": "application/json",
            "X-API-KEY": self.__api_key,
            "User-Agent": "reports-service-layer",
        }

        url = f"{self.__reports_url}/{self.__endpoint}"
        self.logger.debug("Sending POST request to %s with data: %s items", url, len(data))

        session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["POST"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        resp = session.post(url, headers=headers, json=data,
                            timeout=180, stream=True).status_code
        if resp != 200:
            self.logger.error("Failed POST request to %s. Received status: %s", url, resp)
        else:
            self.logger.debug("Successful POST request to %s", url)
        return resp
