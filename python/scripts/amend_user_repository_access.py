import logging

from python.lib.organisation import Organisation
from python.lib.constants import Constants
from python.services.GithubService import GithubService

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    level=logging.WARNING,
    datefmt="%Y-%m-%d %H:%M:%S",
)


def main():
    print("Start")
    constants = Constants()
    oauth_token = constants.get_oauth_token()
    org_name = constants.get_org_name()
    github_service = GithubService(oauth_token, org_name)
    org = Organisation(github_service, org_name)
    org.check_users_access()
    print("Finished")


if __name__ == "__main__":
    main()
