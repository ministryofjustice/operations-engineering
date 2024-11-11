from datetime import datetime, timedelta
from services.github_service import GithubService
from services.slack_service import SlackService
from config.constants import MINISTRY_OF_JUSTICE
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

    github_username = 'AntonyBishop'

    today = datetime.now()
    one_week_ago = (today - timedelta(days=7)).strftime('%Y-%m-%d')

    removed_users_entries = moj_github_org_service.get_user_removal_events(one_week_ago, github_username)

    removed_usernames = [entry['userLogin'].lower() for entry in removed_users_entries]

    current_members = [username.lower() for username in moj_github_org_service.get_org_members_login_names()]

    users_rejoined = [username for username in removed_usernames if username in current_members]

    total_removed = len(removed_usernames)
    total_rejoined = len(users_rejoined)

    if total_removed == 0:
        error_rate = 0

    else:
        error_rate = round((total_rejoined / total_removed) * 100, 2)

    SlackService(env.get("ADMIN_SLACK_TOKEN")).send_github_rejoin_report(total_removed, total_rejoined, error_rate)


if __name__ == '__main__':
    main()
