import os
import sys
import time
import traceback

from python.services.github_service import GithubService


def print_stack_trace(message):
    """Print a stack trace when an exception occurs

    Args:
        message (string): A message to print when exception occurs
    """
    print(message)
    try:
        exc_info = sys.exc_info()
    finally:
        traceback.print_exception(*exc_info)
        del exc_info


def run(github_service: GithubService):
    """A function for the main functionality of the script"""

    try:
        gh = github_service.github_client_core_api
        org = gh.get_organization("moj-analytical-services")
        team_id = github_service.get_team_id_from_team_name("everyone")
        gh_team = org.get_team(team_id)
        all_org_members = gh_team.get_members()
        org_members = org.get_members()
        for member in org_members:
            if member not in all_org_members:
                print(member)
                gh_team.add_membership(member)
                # Delay for GH API
                time.sleep(3)
    except Exception:
        message = "Warning: Exception in Run()"
        print_stack_trace(message)


def main():
    org_token = os.getenv("ADMIN_GITHUB_TOKEN")
    if not org_token:
        raise ValueError(
            "The env variable ADMIN_GITHUB_TOKEN is empty or missing")
    github_service = GithubService(org_token, "moj-analytical-services")
    print("Start")
    run(github_service)
    print("Finished")


if __name__ == "__main__":
    main()
