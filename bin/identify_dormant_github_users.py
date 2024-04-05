from services.github_service import GithubService

DORMANT_USER_THRESHOLD = 90


def setup_environment() -> tuple[str, str]:
    # get tokens from environment variables
    return "github_token", "auth0_token"


def get_audit_logs() -> list[str]:
    # get github and auth0 audit logs
    return ["user1", "user2", "user3"]


def identify_dormant_users(github_users: list[str], audit_logs: list[str]) -> list[str]:
    # identify users that don't appear in the logs
    return ["user1", "user2", "user3"]


def identify_dormant_github_users():
    github_token, auth0_token = setup_environment()

    github = GithubService(github_token, "ministryofjustice")
    all_users = github.get_users_of_multiple_organisations(["ministryofjustice", "moj-analytical-services"])

    active_github_users = github.get_audit_log_active_users()
    # get list of all users from both organisations
    # get github and auth0 audit logs
    # identify users that don't appear in the logs
    # print the users


if __name__ == "__main__":
    identify_dormant_github_users()