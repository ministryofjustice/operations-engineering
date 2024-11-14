import os
from datetime import datetime, timedelta
from config.constants import MINISTRY_OF_JUSTICE, MINISTRY_OF_JUSTICE_TEST
import time
from operator import itemgetter

from services.github_service import GithubService


def main():

    gh_admin_token = os.getenv("GH_ADMIN_TOKEN")
    if not gh_admin_token:
        raise Exception("ADMIN_GITHUB_TOKEN must be set")

    gh = GithubService(str(gh_admin_token), MINISTRY_OF_JUSTICE_TEST)
    # gh = GithubService(str(gh_admin_token), MINISTRY_OF_JUSTICE)

    # Create set of current user logins
    current_users_set = gh.get_current_user_logins()
    # Ignore set
    ignore_set = {"moj-operations-engineering-bot"}


    # Get list of dictionaries of active repos and their current contributors
    repos_and_current_contributors = gh.get_current_contributors_for_active_repos()
    print("\nRepos and current contributors:")
    print(repos_and_current_contributors)

    users_to_check = list(current_users_set - ignore_set)

    dormant_users = []
    since_datetime=datetime(2023, 8, 7)
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
            dormant_users.append(login)
        print(f"{login} has made commits since {since_datetime}: {commits}")
        count += 1

    print(f"\nDormant users: {dormant_users}")
    print(f"Active users: {set(users_to_check) - set(dormant_users)}")


if __name__ == "__main__":
    start = time.time()
    main()
    end = time.time()
    print(f"\nTime taken: {(end-start) / 60} minutes")
