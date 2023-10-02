import os

from python.lib.organisation import Organisation
from python.services.github_service import GithubService


# Refactor Status: Done
# Moved to functionalit to close_move_users_to_teams_expired_issues_refactor.py
# TODO: Delete this file and remove the config file from the GH Action
def main():
    print("Start")

    oauth_token = os.getenv("ADMIN_GITHUB_TOKEN")
    if not oauth_token:
        raise ValueError(
            "The env variable ADMIN_GITHUB_TOKEN is empty or missing")

    moj_github_service = GithubService(oauth_token, "ministryofjustice")
    moj_org = Organisation(moj_github_service, "ministryofjustice")
    moj_org.close_expired_issues()

    as_github_service = GithubService(oauth_token, "moj-analytical-services")
    as_org = Organisation(as_github_service, "moj-analytical-services")
    as_org.close_expired_issues()

    print("Finished")


if __name__ == "__main__":
    main()
