import os

from services.github_service import GithubService

ORGANISATION = "ministryofjustice"
REPOSITORY = "operations-engineering"
SUPPORT_TAG = "Support"


def get_environment_variables() -> str:
    github_token = os.getenv("ADMIN_GITHUB_TOKEN")
    if not github_token:
        raise ValueError(
            "The env variable ADMIN_GITHUB_TOKEN is empty or missing")

    return github_token


def main():
    github_token = get_environment_variables()
    GithubService(github_token, ORGANISATION).close_repository_open_issues_with_tag(
        REPOSITORY, SUPPORT_TAG)


if __name__ == "__main__":
    main()
