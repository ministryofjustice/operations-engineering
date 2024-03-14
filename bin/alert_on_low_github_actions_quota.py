from services.github_service import GithubService
from config.constants import ENTERPRISE, MINISTRY_OF_JUSTICE, SLACK_CHANNEL
import os
import json
from services.slack_service import SlackService
import datetime
import time

def reset_alerting_threshold_if_first_day_of_month(github_service):
    base_alerting_threshold = 70

    if datetime.date.today().day == 1:
        github_service.modify_gha_minutes_quota_threshold(base_alerting_threshold)

def calculate_percentage_used(total_minutes_used):
    total_available = 50000

    return (total_minutes_used / total_available) * 100

def low_threshold_triggered_message(percentage_used):
    return f"Warning:\n\n {round(100 - percentage_used, 1)}% of the Github Actions minutes quota remains."

def calculate_total_minutes_used(organisations, github_service):
    total = 0 
    
    for org in organisations:
        billing_data = github_service.get_gha_minutes_used_for_organisation(org.login)
        processed_data = json.loads(billing_data)
        minutes_used = processed_data["total_minutes_used"]
        total += minutes_used

    return total

def alert_on_low_quota():
    github_token = os.environ.get("GH_TOKEN")
    slack_token = os.environ.get("ADMIN_SLACK_TOKEN")

    github_service = GithubService(github_token, MINISTRY_OF_JUSTICE, ENTERPRISE)
    slack_service = SlackService(slack_token)
    
    organisations = github_service.get_all_organisations_in_enterprise()

    total_minutes_used = calculate_total_minutes_used(organisations, github_service)

    percentage_used = calculate_percentage_used(total_minutes_used)

    reset_alerting_threshold_if_first_day_of_month(github_service)

    threshold = github_service.get_gha_minutes_quota_threshold()

    if percentage_used >= threshold:
        slack_service.send_message_to_plaintext_channel_name(low_threshold_triggered_message(percentage_used), SLACK_CHANNEL)
        github_service.modify_gha_minutes_quota_threshold(threshold + 10)


if __name__ == "__main__":
    alert_on_low_quota()


