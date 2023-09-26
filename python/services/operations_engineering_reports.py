import requests
import logging
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


class OperationsEngineeringReportsService:
    """Communicate with the operations-engineering-reports API. This service is used to send reports
    to the API, which will then be displayed on the reports page.

    Arguments:
        url {str} -- The url of the operations-engineering-reports API.
        endpoint {str} -- The endpoint of the operations-engineering-reports API.
        api_key {str} -- The API key to use for the operations-engineering-reports API.

    """

    def __init__(self, url: str, endpoint: str, api_key: str, log_level: str) -> None:
        self.__reports_url = url
        self.__endpoint = endpoint
        self.__api_key = api_key

        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(log_level)
        self.logger.info(
            f"Initialised {self.__class__.__name__}  \
            with url:  {self.__reports_url},  \
            endpoint: {self.__endpoint}"
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
        #  The database can't handle more than 100 at a time
        # so we need to chunk the list into 100s.
        self.logger.info("fSending {len(reports)} repository standards reports to API.")
        for i in range(0, len(reports), 100):
            chunk = reports[i:i+100]
            status = self.__http_post(chunk)
            if status != 200:
                self.logger.error(f"Failed to send chunk starting from index {i}. Received status: {status}")
                raise ValueError(
                    f"Failed to send repository standards reports to API. Received: {status}")
            else:
                self.logger.debug(f"Successfully sent chunk starting from index {i}")

    def __http_post(self, data: list[dict]) -> int:
        headers = {
            "Content-Type": "application/json",
            "X-API-KEY": self.__api_key,
            "User-Agent": "reports-service-layer",
        }

        url = f"{self.__reports_url}/{self.__endpoint}"
        self.logger.debug(f"Sending POST request to {url} with data: {len(data)} items")

        session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[500, 502, 503, 504],
            method_whitelist=["POST"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        resp = session.post(url, headers=headers, json=data,
                            timeout=180, stream=True).status_code
        if resp != 200:
            self.logger.error(f"Failed POST request to {url}. Received status: {resp}")
        else:
            self.logger.debug(f"Successful POST request to {url}")
        return resp
