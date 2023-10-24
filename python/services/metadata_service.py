import requests
import logging


class MetadataService:
    def __init__(self, api_url: str, api_token: str):
        self.api_url = api_url
        self.api_token = api_token

    def get_acceptable_slack_users(self):
        return [
            {"username": "sam.pepper"},
            {"username": "connor.glynn"}
        ]

    def get_acceptable_github_usernames(self):
        return [
            {"username": "PepperMoJ"},
            {"username": "connormaglynn"}
        ]

    def get_existing_slack_users(self):
        response = requests.get(
            f"{self.api_url}/slack_users", headers={"Authorization": f"Bearer {self.api_token}"})
        if response.status_code == 200:
            return response.json()
        else:
            logging.error(
                "Error fetching existing Slack usernames: %s", response.content)
            return []

    def filter_usernames(self, username_list: list[dict], accepted_username_list: list[dict]):
        """Filter out all usernames deemed not acceptable.

        Parameters:
            username_list: Initial list containing all usernames
            accepted_username_list: A list of acceptable usernames to include in the final list

        Returns:
            filtered_usernames: A list of filtered usernames
        """

        accepted_usernames_set = {user["username"]
                                  for user in accepted_username_list}

        filtered_usernames = [
            user for user in username_list if user["username"] in accepted_usernames_set
        ]

        return filtered_usernames

    def combine_user_data(self, slack_user_data: list[dict], github_user_data: list[dict]):
        """Combine user data from Slack and GitHub based on the email address

        Parameters:
            slack_user_data: A list of dictionaries containing Slack usernames and emails
            github_user_data: A list of dictionaries containing GitHub usernames and emails

        Returns:
            list: A list of dictionaries containing combined user data.
        """

        combined_user_data = []

        github_email_to_username = {
            user['email']: user['username'] for user in github_user_data}

        for slack_user in slack_user_data:
            email = slack_user['email']
            if email in github_email_to_username:
                combined_user = {
                    "slack_username": slack_user['username'],
                    "github_username": github_email_to_username[email],
                    "email": email,
                }
                combined_user_data.append(combined_user)

        return combined_user_data

    def add_new_usernames(self, usernames_to_add: list[dict]):
        """Send list of new usernames to be added to the Metadata API

        Parameters:
            usernames_to_add: A list of all new usernames to add

        Returns:
            list: None
        """
        payload = {"users": usernames_to_add}

        response = requests.post(
            f"{self.api_url}/user/add",
            json=payload,
        )

        if response.status_code == 200 or response.status_code == 201:
            logging.info("New usernames added successfully!")
        else:
            logging.error(
                "Error adding new usernames: %s", response.content)
