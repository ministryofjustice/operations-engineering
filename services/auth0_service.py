import logging
import time
from datetime import datetime, timedelta

import requests

RESPONSE_OKAY = 200
RESPONSE_NO_CONTENT = 204
logging.basicConfig(level=logging.INFO)


class Auth0Service:
    def __init__(self, client_secret: str, client_id: str, domain: str, grant_type: str = 'client_credentials'):
        """
        Args:
            client_secret (str): Client Secret from Auth0
            client_id (str): Client ID from Auth0
            domain (str): Domain from Auth0
            grant_type (str, optional): Grant type used to acquire access token. Defaults to 'client_credentials'.
        """
        self.client_secret = client_secret
        self.client_id = client_id
        self.domain = domain
        self.audience = f"https://{domain}/api/v2/"
        self.grant_type = grant_type
        self.access_token = self.get_access_token()

    def _make_request(self, method: str, endpoint: str, data: dict[str, any] = None) -> requests.Response:
        """Base request utility function

        Args:
            method (str): API method to use
            endpoint (str): API endpoint to use
            data (dict[str, any], optional): Body data to use, defaults to None

        Raises:
            Exception: If the request fails

        Returns:
            requests.Response: Response object
        """

        logging.debug("Making %s request to %s", method, endpoint)

        # Create endpoint URL and headers using domain and access token
        url = f"https://{self.domain}/{endpoint}"
        headers = {'content-type': 'application/json',
                   'Authorization': f'Bearer {self.access_token}'}

        if data is not None:
            # Makes a request based on the given method, URL, headers and data
            response = requests.request(
                method, url, json=data, headers=headers, timeout=10)
        else:
            # Makes a request based on the given method, URL and headers only
            response = requests.request(
                method, url, headers=headers, timeout=10)

        return response

    def get_access_token(self) -> str:
        """Gets an access token from Auth0

        Raises:
            Exception: If the request fails

        Returns:
            str: Access token
        """

        logging.info("Getting access token from Auth0")

        # Create endpoint URL and headers using domain and access token
        url = f"https://{self.domain}/oauth/token"
        headers = {'content-type': 'application/json'}

        # Create body data
        payload = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'audience': self.audience,
            'grant_type': self.grant_type
        }

        # Makes request
        response = requests.post(
            url, json=payload, headers=headers, timeout=10)

        if response.status_code == RESPONSE_OKAY:
            logging.info("Access token received")
            # Returns the received access token.
            return response.json()['access_token']

        logging.error(
            "Failed to get access token from Auth0: %s", response.text)
        raise Exception("Failed to get access token from Auth0")

    def _get(self, endpoint: str) -> requests.Response:
        """Sends a GET request to the API endpoint.

        Args:
            endpoint (str): Auth0 API endpoint to send the request to.

        Returns:
            requests.Response: Response object
        """
        logging.debug("Getting data from %s", endpoint)
        return self._make_request('GET', endpoint)

    def _delete(self, endpoint: str) -> requests.Response:
        """Sends a DELETE request to the API endpoint.

        Args:
            endpoint (str): API endpoint to send the request to.

        Returns:
            requests.Response: Response object
        """
        logging.debug("Deleting data from %s", endpoint)
        return self._make_request('DELETE', endpoint)

    def delete_inactive_users(self, days_inactive: int = 90) -> None:
        self._delete_users(self.get_inactive_users(days_inactive))

    def _delete_users(self, users: list[dict[str, any]]) -> None:
        for user in users:
            logging.debug("Deleting user %s", user['user_id'])
            self.delete_user(user['user_id'])

    def delete_user(self, user_id: str) -> requests.Response:
        """Deletes a user from Auth0

        Args:
            user_id (str): ID of the user in Auth0

        Returns:
            requests.Response: Response object
        """
        response = self._delete(f'api/v2/users/{user_id}')

        if response.status_code == RESPONSE_NO_CONTENT:
            logging.info("User %s deleted", user_id)
        else:
            logging.error("Failed to delete user %s: %s",
                          user_id, response.text)

        time.sleep(1)

        return response.status_code

    def _get_users(self, page=0, per_page=100) -> list[dict[str, any]]:
        """Gets all users from Auth0

        Args:
            page (int, optional): Page number to retrieve. Defaults to 0.
            per_page (int, optional): Number of users to retrieve per page. Defaults to 100.

        Returns:
            list[dict[str, any]]: A dictionary containing all users
        """

        # List to hold users
        all_users = []

        # Paginate through users
        while True:
            response = self._get(
                f'api/v2/users?page={page}&per_page={per_page}')
            if response.status_code == RESPONSE_OKAY:
                users = response.json()
                logging.debug("Users retrieved")
                for user in users:
                    all_users.append(user)
                # Out of users
                if len(users) < per_page:
                    break
                page += 1
                time.sleep(0.5)
            else:
                logging.error("Failed to get users: %s", response.text)
                break

        return all_users

    def get_inactive_users(self, days_inactive: int = 90) -> list[dict[str, any]]:
        """Gets all users who have not logged in for a given number of days

        Args:
            days_inactive (int, optional): how many days is classed as inactive. Defaults to 90.

        Returns:
            list[dict[str, any]]: List of users
        """

        def is_user_inactive(user: dict) -> bool:
            """Check if a user is inactive.

            A user is considered inactive if they have never logged in or their last login was more than `days_inactive` days ago.

            Args:
                user (dict): The user to check.

            Returns:
                bool: True if the user is inactive, False otherwise.
            """
            last_login_str = user.get('last_login')
            if last_login_str is None:
                # User has never logged in
                return True

            last_login = datetime.strptime(
                last_login_str, '%Y-%m-%dT%H:%M:%S.%fZ')
            return last_login < (datetime.utcnow() - timedelta(days=days_inactive))

        return [user for user in self._get_users() if is_user_inactive(user)]

    def get_active_users(self, days_inactive: int = 90) -> list[dict[str, any]]:
        """Gets all users who have logged in for a given number of days

        Args:
            days_inactive (int, optional): how many days is classed as inactive. Defaults to 90.

        Returns:
            list[dict[str, any]]: list of users
        """

        # List to hold active users
        users2 = []
        for user in self._get_users():
            if user.get('last_login'):
                last_login = datetime.strptime(
                    user['last_login'], '%Y-%m-%dT%H:%M:%S.%fZ')
                if last_login > (datetime.utcnow() - timedelta(days=days_inactive)):
                    users2.append(user)
        return users2

    def get_active_users_usernames(self) -> list[str]:
        return [user["nickname"].lower() for user in self.get_active_users()]

    def get_active_case_sensitive_usernames(self) -> list[str]:
        return [user["nickname"] for user in self.get_active_users()]
