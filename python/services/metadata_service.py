import requests
import logging


class MetadataService:
    def __init__(self, api_url: str, api_token: str):
        self.api_url = api_url
        self.api_token = api_token

    def get_acceptable_slack_users(self):
        return [
            {"username": "sam.pepper"}
        ]

    def get_existing_slack_users(self):
        try:
            response = requests.get(
                f"{self.api_url}/slack_users", headers={"Authorization": f"Bearer {self.api_token}"})
            if response.status_code == 200:
                return response.json()
            else:
                logging.error(
                    "Error fetching existing Slack usernames: %s", response.content)
                return []
        except Exception as e:
            logging.error(
                "An error occurred while fetching existing Slack usernames: %s", str(e))
            return []

    def add_new_slack_usernames(self, usernames_to_add: list[dict]):
        payload = {"usernames_to_add": usernames_to_add}

        try:
            response = requests.post(
                f"{self.api_url}/add_slack_users",
                json=payload,
                headers={"Authorization": f"Bearer {self.api_token}"}
            )

            if response.status_code == 200 or response.status_code == 201:
                logging.info("New Slack usernames added successfully!")
            else:
                logging.error(
                    "Error adding new Slack usernames: %s", response.content)
        except Exception as e:
            logging.error(
                "An error occurred while adding new Slack usernames: %s", str(e))
