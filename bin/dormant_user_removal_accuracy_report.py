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
    ap_github_org_service = GithubService(env.get(
        "GH_AP_ADMIN_TOKEN"), MOJ_ANALYTICAL_SERVICES)

    github_username = 'AntonyBishop'

    today = datetime.now()
    one_week_ago = (today - timedelta(days=7)).strftime('%Y-%m-%d')

    removed_users_entries_moj = moj_github_org_service.get_user_removal_events(one_week_ago, github_username)
    removed_users_entries_ap = ap_github_org_service.get_user_removal_events(one_week_ago, github_username)

    removed_usernames_moj = [entry['userLogin'].lower() for entry in removed_users_entries_moj]
    removed_usernames_ap = [entry['userLogin'].lower() for entry in removed_users_entries_ap]

    current_members_moj = [username.lower() for username in moj_github_org_service.get_org_members_login_names()]
    current_members_ap = [username.lower() for username in ap_github_org_service.get_org_members_login_names()]

    users_rejoined_moj = [username for username in removed_usernames_moj if username in current_members_moj]
    users_rejoined_ap = [username for username in removed_usernames_ap if username in current_members_ap]

    total_removed_moj = len(removed_usernames_moj)
    total_rejoined_moj = len(users_rejoined_moj)

    total_removed_ap = len(removed_usernames_ap)
    total_rejoined_ap = len(users_rejoined_ap)

    if total_removed_moj and total_removed_ap == 0:
        error_rate_moj = 0
        error_rate_ap = 0

    else:
        error_rate_moj = round((total_rejoined_moj / total_removed_moj) * 100, 2)
        error_rate_ap = round((total_rejoined_ap / total_removed_ap) * 100, 2)

    SlackService(env.get("ADMIN_SLACK_TOKEN")).send_github_rejoin_report(
      total_removed_moj,
      total_removed_ap,
      total_rejoined_moj,
      total_rejoined_ap,
      error_rate_moj,
      error_rate_ap)

if __name__ == '__main__':
    main()
