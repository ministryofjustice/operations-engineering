import os

from python.services.slack_service import SlackService
from python.services.metadata_service import MetadataService
from python.services.github_service import GithubService


def get_environment_variables() -> tuple:
    slack_token = os.getenv("ADMIN_SLACK_TOKEN")
    if not slack_token:
        raise ValueError(
            "The env variable ADMIN_SLACK_TOKEN is empty or missing")
    github_token = os.getenv("ADMIN_GITHUB_TOKEN")
    if not github_token:
        raise ValueError(
            "The env variable ADMIN_GITHUB_TOKEN is empty or missing")
    api_url = os.getenv("METADATA_API_URL")
    if not api_url:
        raise ValueError(
            "The env variable METADATA_API_URL is empty or missing")
    api_token = os.getenv("METADATA_API_TOKEN")
    if not api_token:
        raise ValueError(
            "The env variable METADATA_API_TOKEN is empty or missing")

    return slack_token, github_token, api_url, api_token


def main():

    slack_token, github_token, api_url, api_token = get_environment_variables()

    slack_service = SlackService(slack_token)
    metadata_service = MetadataService(api_url, api_token)
    github_service = GithubService(github_token, "ministryofjustice")

    # Grabs a list of all slack usernames from the Slack API (using stub for testing purposes)
    slack_usernames = slack_service.get_all_slack_usernames_stub()
    
    # Grabs a list of all GitHub usernames from the GitHub API (using stub for testing purposes)
    github_usernames = github_service.get_all_github_usernames_stub()
    
    print(f"<PEPPER> - Slack usernames: {slack_usernames}")
    print(f"<PEPPER> - GitHub usernames: {github_usernames}")

    # Grabs a list of acceptable slack usernames (this is for testing purposes)
    acceptable_slack_users = metadata_service.get_acceptable_slack_users()
    
    # Grabs a list of acceptable github usernames (this is for testing purposes)
    acceptable_github_users = metadata_service.get_acceptable_github_usernames()
    
    print(f"<PEPPER> - Acceptable slack usernames: {acceptable_slack_users}")
    print(f"<PEPPER> - Acceptable gitHub usernames: {acceptable_github_users}")

    # Filter the full list of Slack users to only include some defaults
    filtered_slack_usernames = slack_service.filter_usernames(
        slack_usernames, acceptable_slack_users)
    
    # Filter the full list of GitHub users to only include the defaults
    filtered_github_usernames = slack_service.filter_usernames(
        github_usernames, acceptable_github_users)
    
    print(f"<PEPPER> - Filtered slack usernames: {filtered_slack_usernames}")
    print(f"<PEPPER> - Filtered gitHub usernames: {filtered_github_usernames}")
    
    # Combine both slack and GitHub user lists
    combined_user_information = metadata_service.combine_user_data(filtered_github_usernames, filtered_slack_usernames)
    
    print(f"<PEPPER> - Combined user information: {filtered_github_usernames}")

    # Send the new Slack usernames to the metadata API to be added into the database
    # metadata_service.add_new_usernames(combined_user_information)


if __name__ == "__main__":
    main()
