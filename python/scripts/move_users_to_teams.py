import os
import logging

from python.lib.organisation import Organisation
from python.services.github_service import GithubService

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    level=logging.WARNING,
    datefmt="%Y-%m-%d %H:%M:%S",
)


def main():
    print("Start")

    org_name = os.getenv("ORG_NAME")
    if not org_name:
        raise ValueError("The env variable ORG_NAME is empty or missing")

    oauth_token = os.getenv("ADMIN_GITHUB_TOKEN")
    if not oauth_token:
        raise ValueError(
            "The env variable ADMIN_GITHUB_TOKEN is empty or missing")

    github_service = GithubService(oauth_token, org_name)
    org = Organisation(github_service, org_name)
    org.move_users_to_teams()
    org.close_expired_issues()
    print("Finished")


if __name__ == "__main__":
    main()
