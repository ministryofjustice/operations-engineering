import os
from services.github_service import GithubService


def get_environment_variables() -> str:
    github_token = os.getenv("ADMIN_GITHUB_TOKEN")
    if not github_token:
        raise ValueError(
            "The env variable ADMIN_GITHUB_TOKEN is empty or missing")

    return github_token

# Function to remove the identified stale outside collaborators - also to go in github service
# def remove_collaborator(collaborator, github_service: GithubService):
#     """Remove the collaborator from the organisation
#     Args:
#         collaborator (collaborator): The collaborator object
#     """
#     logging.info(f"Remove user from organisation: {collaborator.login}")
#     org = github_service.github_client_core_api.get_organization(
#         "ministryofjustice")
#     org.remove_outside_collaborator(collaborator)

# ToDo
# tests for github service functions and main
# workflow update; remove on PR trigger
# delete old scripts and workflow
# names check over
# update PR
# line 701 TestGithubServiceGetPaginatedListOfUnlockedUnarchivedReposAndOutsideCollaborators
# test for TestGithubServiceGetStaleOutsideCollaborators line 1268 in test_github_service
# Add remove outside collaborator function to github service - or is this usng the
# test for remove_outside_collaboraotr, does it just accept string of coolab name?

def main():
    github_token = get_environment_variables()
    github = GithubService(github_token, "ministryofjustice")

    stale_outside_collaborators = github.get_stale_outside_collaborators()
    print(f"Stale Outside Collaborators:\n{stale_outside_collaborators}")
    print(f"Number of Stale Outside Collaborators to remove: {len(stale_outside_collaborators)}")

    # Remove the stale outside collaborators
    # for stale_outside_collaborator in stale_outside_collaborators:
    #     github.remove_outside_collaborator_from_org(stale_outside_collaborator)

    return stale_outside_collaborators


if __name__ == "__main__":
    main()
