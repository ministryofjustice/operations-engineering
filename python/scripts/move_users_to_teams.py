import logging

from python.lib.organisation import Organisation
from python.lib.constants import Constants
from python.services.github_service import GithubService

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    level=logging.WARNING,
    datefmt="%Y-%m-%d %H:%M:%S",
)


def main():
    print("Start")
    constants = Constants()
    github_service = GithubService(constants.oauth_token, constants.org_name)
    org = Organisation(github_service, constants.org_name)
    org.check_users_access()
    print("Finished")


if __name__ == "__main__":
    main()
