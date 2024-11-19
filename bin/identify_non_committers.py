import os
from datetime import datetime, timedelta
from config.constants import MINISTRY_OF_JUSTICE, MINISTRY_OF_JUSTICE_TEST, MOJ_ANALYTICAL_SERVICES
import time
from operator import itemgetter

from services.github_service import GithubService

def get_environment_variables() -> tuple:
    gh_token = os.getenv("GH_ADMIN_TOKEN")
    if not gh_token:
        raise ValueError(
            "The env variable GH_ADMIN_TOKEN is empty or missing")
    return gh_token

def main():

    gh_token = get_environment_variables()
    # gh = GithubService(str(gh_token), MINISTRY_OF_JUSTICE)
    # gh = GithubService(str(gh_token), MOJ_ANALYTICAL_SERVICES)

    gh = GithubService(gh_token, MINISTRY_OF_JUSTICE_TEST)

    # Create set of current user logins
    # current_users_set = set(gh.get_org_members_login_names())
    # Ignore set
    # ignore_set = {"moj-operations-engineering-bot"}

    # Get list of dictionaries of active repos and their current contributors
    repos_and_current_contributors = gh.get_current_contributors_for_active_repos()
    print("\nRepos and current contributors:")
    print(repos_and_current_contributors)

    # Feed users to check here
    users_to_check = [user.login for user in gh._GithubService__get_all_users()]

    print(users_to_check)
    non_committers = []
    since_datetime=datetime(2023, 8, 1)
    count = 1
    number_of_users = len(users_to_check)

    for login in users_to_check:
        print(f"\nChecking user {count} of {number_of_users}")
        commits = gh.user_has_commmits_since(
            login=login,
            repos_and_contributors=repos_and_current_contributors,
            since_datetime=since_datetime
        )
        if not commits:
            non_committers.append(login)
        print(f"{login} has made commits since {since_datetime}: {commits}")
        count += 1

    print(f"\nNon-committers since {since_datetime}: {non_committers}")
    print(f"Active committers since {since_datetime}: {set(users_to_check) - set(non_committers)}")


if __name__ == "__main__":
    start = time.time()
    main()
    end = time.time()
    print(f"\nTime taken: {(end-start) / 60} minutes")
