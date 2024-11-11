import logging
from datetime import datetime, timedelta
from services.github_service import GithubService
from services.slack_service import SlackService
from config.constants import ENTERPRISE, MINISTRY_OF_JUSTICE, MOJ_ANALYTICAL_SERVICES
from utils.environment import EnvironmentVariables


def main():

    required_env_vars = [
        "GH_MOJ_ADMIN_TOKEN",
        "GH_AP_ADMIN_TOKEN",
        "ADMIN_SLACK_TOKEN",
        "GH_GITHUB_TOKEN_AUDIT_LOG_TOKEN"
    ]

    env = EnvironmentVariables(required_env_vars)

    moj_github_org_service = GithubService(env.get(
        "GH_GITHUB_TOKEN_AUDIT_LOG_TOKEN"), MINISTRY_OF_JUSTICE)
    # ap_github_org_service = GithubService(env.get(
    #     "GH_AP_ADMIN_TOKEN"), MOJ_ANALYTICAL_SERVICES)

    # Configure logging
    logging.basicConfig(level=logging.INFO)

    github_username = 'AntonyBishop'

    today = datetime.now()
    one_week_ago = (today - timedelta(days=7)).strftime('%Y-%m-%d')

    removed_users_entries = moj_github_org_service.get_user_removal_events(one_week_ago, github_username)

    removed_usernames = [entry['userLogin'].lower() for entry in removed_users_entries]
    logging.info("Users removed by %s in the last week: %s", github_username, removed_usernames)

    current_members = [username.lower() for username in moj_github_org_service.get_org_members_login_names()]

    users_rejoined = [username for username in removed_usernames if username in current_members]
    logging.info("Users who have rejoined: %s", users_rejoined)

    total_removed = len(removed_usernames)
    total_rejoined = len(users_rejoined)

    if total_removed == 0:
        error_rate = 0
    else:
        error_rate = round((total_rejoined / total_removed) * 100, 2)

    result_message = (
        f"Total users removed by {github_username} in the last week: {total_removed}\n"
        f"Total users who have rejoined: {total_rejoined}\n"
        f"Percentage of users removed in error: {error_rate}%"
    )

    SlackService(env.get("ADMIN_SLACK_TOKEN")).send_github_rejoin_report(total_removed, total_rejoined, error_rate, MINISTRY_OF_JUSTICE)

    logging.info(result_message)


if __name__ == '__main__':
    main()
