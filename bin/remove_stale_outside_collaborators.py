import os
from services.github_service import GithubService


def get_environment_variables() -> str:
    github_token = os.getenv("ADMIN_GITHUB_TOKEN")
    if not github_token:
        raise ValueError(
            "The env variable ADMIN_GITHUB_TOKEN is empty or missing")

    return github_token

def main():
    github_token = get_environment_variables()
    github = GithubService(github_token, "ministryofjustice")

    stale_outside_collaborators = github.get_stale_outside_collaborators()
    print(f"Stale Outside Collaborators:\n{stale_outside_collaborators}")
    print(f"Number of Stale Outside Collaborators to remove: {len(stale_outside_collaborators)}")

    # need some logging - log who is being removed? Iis it ok to print this out to console?
    for stale_outside_collaborator in stale_outside_collaborators:
        github.remove_outside_collaborator_from_org(stale_outside_collaborator)

    return stale_outside_collaborators


if __name__ == "__main__":
    main()
