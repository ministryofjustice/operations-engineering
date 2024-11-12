import os
from datetime import datetime, timedelta
from config.constants import MINISTRY_OF_JUSTICE, MINISTRY_OF_JUSTICE_TEST
import time
from operator import itemgetter

from services.github_service import GithubService


def _calculate_date(in_last_days: int) -> str:
    current_date = datetime.now()
    date = current_date - timedelta(days=in_last_days)
    timestamp_format = "%Y-%m-%d"
    return date.strftime(timestamp_format)



def main():

    gh_admin_token = os.getenv("GH_ADMIN_TOKEN")
    if not gh_admin_token:
        raise Exception("ADMIN_GITHUB_TOKEN must be set")

    # gh = GithubService(str(gh_admin_token), MINISTRY_OF_JUSTICE_TEST)
    gh = GithubService(str(gh_admin_token), MINISTRY_OF_JUSTICE)

    # Create set of current user logins
    current_users_set = gh.get_current_user_logins()


    # Get list of dictionaries of active repos and their current contributors
    repos_and_current_contributors = gh.get_current_contributors_for_active_repos()
    print("\nRepos and current contributors:")
    print(repos_and_current_contributors)

    # Initiate the active_user set with bot accounts
    active_users = {"moj-operations-engineering-bot"}
    print(f"\nActive users starting ignore set: {active_users}")
    since_datetime = datetime(2024, 8, 7)
    number_of_repos = len(repos_and_current_contributors)
    count = 1

    for repo_object in repos_and_current_contributors:
        repo_name = repo_object.get('repository')
        print(f"\nGetting commits since {since_datetime} for repository {repo_name}: number {count} out of {number_of_repos}")

        # Remove known active contributors
        contributors_less_active_users = repo_object.get("contributors") - active_users
        print(f"Removed known committers from contributor check set for repo: {repo_name}")

        # Get commits for remaining contributors to determine if they are active
        active_repo_committers = gh.get_repo_committers_since(
            repo_name=repo_object.get("repository"),
            contributors=contributors_less_active_users,
            since_datetime=since_datetime,
        )
        if active_repo_committers:
            active_users = active_users.union(active_repo_committers)
        count += 1

    print(f"\nFinal active user set:\n{active_users}")

    # Get contributors who have not committed since the given date
    non_committers = current_users_set - active_users
    print(f"\nFinal non-committers set to be removed:\n{non_committers}")

    return non_committers



if __name__ == "__main__":
    start = time.time()
    main()
    end = time.time()
    print(f"\nTime taken: {(end-start) / 60} minutes")
