import logging
import os
import time
from datetime import datetime

from dateutil.relativedelta import relativedelta

from python.lib.moj_archive import MojArchive
from python.lib.moj_github import MojGithub


# This file assigns archives all repositories which have had no commits from a certain datetime
# The goal is clean the ministryofjustice GitHub organization.

def get_commit(repository):
    """get the last commit from a repository

    Args:
        repository (Repository): the repository object

    Returns:
        Commit: if commit exists return the last commit
    """
    # Try block needed as get_commits() can cause exception when
    # a repository has no commits as GH returns negative result.
    try:
        commits = repository.get_commits()
        return commits[0]
    except Exception:
        return 0


def ready_for_archiving(repository, archive_date) -> bool:
    """See if repository is ready for archiving based on last commit date

    Args:
        repository (Repository): the repository object
        archive_date (datetime): the archive date

    Returns:
        bool: true if the last commit date is longer than the archive date
    """
    commit = get_commit(repository)
    if commit == 0:
        print("Manually check repository: " + repository.name)
    else:
        if commit.commit.author.date < archive_date:
            time.sleep(1)
            return True
    return False


def main():
    # Logging Config
    logging.basicConfig(
        format="%(asctime)s %(levelname)-8s %(message)s",
        level=logging.INFO,
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # TODO: Change this to point at a different GitHub organization
    organization = "ministryofjustice"
    org_token = os.getenv("ADMIN_GITHUB_TOKEN")
    if not org_token:
        raise ValueError(
            "The env variable ADMIN_GITHUB_TOKEN is empty or missing")

    # How long ago in which the repositories should be archived
    archive_date_days = 0
    archive_date_months = 6
    archive_date_years = 1

    archive_date = datetime.now() - relativedelta(
        days=archive_date_days, months=archive_date_months, years=archive_date_years
    )

    # Create MoJGithub object
    moj_gh = MojGithub(org=organization, org_token=org_token)

    # Get all repos that need archiving
    repos = [
        repo
        for repo in moj_gh.get_unarchived_repos("public")
        if ready_for_archiving(repo, archive_date)
    ]

    # Print repos
    logging.info(
        f"Beginning archive of inactive repositories for GitHub organization: {organization}"
    )
    logging.info("-----------------------------")
    logging.info(
        f"Searching for inactive repositories from date: {archive_date}")
    logging.info("-----------------------------")

    # Archive repos
    for repo in repos:
        MojArchive(repo).archive()


if __name__ == "__main__":
    main()
