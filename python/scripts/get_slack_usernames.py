import os

from python.services.slack_service import SlackService
from python.services.metadata_service import MetadataService

def get_environment_variables() -> tuple:
    slack_token = os.getenv("ADMIN_SLACK_TOKEN")
    if not slack_token:
        raise ValueError(
            "The env variable ADMIN_SLACK_TOKEN is empty or missing")
    api_url = os.getenv("METADATA_API_URL")
    if not api_url:
        raise ValueError(
            "The env variable METADATA_API_URL is empty or missing")
    api_token = os.getenv("METADATA_API_TOKEN")
    if not api_token:
        raise ValueError(
            "The env variable METADATA_API_TOKEN is empty or missing")

    return slack_token, api_url, api_token

def main():

    slack_token, api_url, api_token = get_environment_variables()
    
    slack_service = SlackService(slack_token)
    metadata_service = MetadataService(api_url, api_token)
    
    # Grabs a list of all slack usernames from the Slack API
    slack_usernames = slack_service.get_all_slack_usernames()
    
    # Grabs the existing Slack usernames from the metadata API (a default list is provided for now)
    existing_slack_users = metadata_service.get_existing_slack_users()
    
    # Filter the full list of Slack users to only include some defaults
    filtered_usernames = slack_service.filter_usernames(slack_usernames, existing_slack_users)
    
    # Send the new Slack usernames to the metadata API to be added into the database
    metadata_service.add_new_slack_usernames(filtered_usernames)


if __name__ == "__main__":
    main()
