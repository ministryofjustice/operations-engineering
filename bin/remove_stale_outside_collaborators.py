import logging
import os
from github import GithubException
from services.github_service import GithubService

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_environment_variables() -> str:
    github_token = os.getenv("ADMIN_GITHUB_TOKEN")
    if not github_token:
        raise ValueError(
            "The env variable ADMIN_GITHUB_TOKEN is empty or missing")

    return github_token

def main():
    github_token = get_environment_variables()
    github = GithubService(github_token, "ministryofjustice")
    org = github.organisation_name

    stale_outside_collaborators = github.get_stale_outside_collaborators()
    for stale_outside_collaborator in stale_outside_collaborators:
        try:
            github.remove_outside_collaborator_from_org(stale_outside_collaborator)
            logger.info(
                "Removed Outside Collaborator %s from %s",
                stale_outside_collaborator,
                org
            )
        except GithubException:
            logger.error(
                "Failed to remove Outside Collaborator %s from %s",
                stale_outside_collaborator,
                org
            )


if __name__ == "__main__":
    main()
