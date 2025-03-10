import logging
import os
import time
from github import GithubException
from config.constants import MINISTRY_OF_JUSTICE, MOJ_ANALYTICAL_SERVICES

from services.github_service import GithubService
from services.slack_service import SlackService
from utils.environment import EnvironmentVariables

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def identify_dormant_outside_collaborators():
    env = EnvironmentVariables(["GH_MOJ_TOKEN", "GH_MOJAS_TOKEN", "ADMIN_SLACK_TOKEN", "DAYS_SINCE"])
    days_since = int(env.get("DAYS_SINCE"))

    gh_orgs = [
        GithubService(env.get("GH_MOJ_TOKEN"), MINISTRY_OF_JUSTICE),
        GithubService(env.get("GH_MOJAS_TOKEN"), MOJ_ANALYTICAL_SERVICES)
    ]

    for gh_org in gh_orgs:
        dormant_outside_collaborators = gh_org.get_dormant_outside_collaborators()

        SlackService(env.get("ADMIN_SLACK_TOKEN")).send_dormant_user_list(dormant_outside_collaborators, str(days_since))


if __name__ == "__main__":
    start = time.time()
    identify_dormant_outside_collaborators()
    end = time.time()
    print(f"\nTime taken: {(end-start) / 60} minutes")

# #  This currently removes dormant OCs -  just want it to identify and post to slack, also post failure to slack
# def get_environment_variables() -> str:
#     github_token = os.getenv("ADMIN_GITHUB_TOKEN")
#     if not github_token:
#         raise ValueError(
#             "The env variable ADMIN_GITHUB_TOKEN is empty or missing")

#     github_organization_name = os.getenv("GITHUB_ORGANIZATION_NAME")
#     if not github_organization_name:
#         raise ValueError(
#             "The env variable GITHUB_ORGANIZATION_NAME is empty or missing")

#     return github_token, github_organization_name


# def main():
#     github_token, github_organization_name = get_environment_variables()
#     github = GithubService(github_token, github_organization_name)
#     dormant_outside_collaborators = github.get_dormant_outside_collaborators()

#     if not dormant_outside_collaborators:
#         logger.info(
#             "No Dormant Outside Collaborators detected."
#         )

#     for dormant_outside_collaborator in dormant_outside_collaborators:
#         try:
#             github.remove_outside_collaborator_from_org(dormant_outside_collaborator)
#             logger.info(
#                 "Removed Outside Collaborator %s from %s",
#                 dormant_outside_collaborator,
#                 github_organization_name
#             )
#         except GithubException:
#             logger.error(
#                 "Failed to remove Outside Collaborator %s from %s",
#                 dormant_outside_collaborator,
#                 github_organization_name
#             )


# if __name__ == "__main__":
#     main()
