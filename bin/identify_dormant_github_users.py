from services.github_service import GithubService
from services.auth0_service import Auth0Service
import sys

DORMANT_USER_THRESHOLD = 90


def setup_environment() -> tuple[str, str]:
    # get tokens from environment variables

    github_token = sys.argv[0]
    auth0_client_secret = sys.argv[1]
    auth0_client_id = sys.argv[2]
    auth0_domain = sys.argv[3]

    return github_token, auth0_client_secret, auth0_client_id, auth0_domain


def get_audit_logs() -> list[str]:
    # get github and auth0 audit logs
    return ["user1", "user2", "user3"]


def identify_dormant_users(github_users: list[str], audit_logs: list[str]) -> list[str]:
    # identify users that don't appear in the logs
    return ["user1", "user2", "user3"]


def identify_dormant_github_users():
    github_token, auth0_client_secret, auth0_client_id, auth0_domain = setup_environment()

    github = GithubService(github_token, "ministryofjustice")

    auth0_service = Auth0Service(
        auth0_client_secret,
        auth0_client_id,
        auth0_domain,
        "client_credentials"
    )

    all_users = github.get_users_of_multiple_organisations(["ministryofjustice", "moj-analytical-services"])

    active_github_users = github.get_audit_log_active_users()

    active_auth0_users = auth0_service.get_active_users()

    dormant_users = [ user for user in all_users if user not in active_github_users and user not in active_auth0_users ]

    # get list of all users from both organisations
    # get github and auth0 audit logs
    # identify users that don't appear in the logs
    # print the users


if __name__ == "__main__":
    identify_dormant_github_users()