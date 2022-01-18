import os
from datetime import datetime
from lib.MojGithub import MojGithub

# This file assigns archives all repositories which have had no commits from a certain datetime
# The goal is clean the ministryofjustice GitHub organization.

# TODO:
# Currently only prints repos, it should archive them
# Whitelist is needed before enabling above ^

## Config
# Change this to point at a different GitHub organization
organization        = "ministryofjustice"
org_token           = os.getenv('ADMIN_GITHUB_TOKEN')

# The date in which repositories should be archived before
archive_date        = "2018-01-17"
archive_date_format = "%Y-%M-%d"
archive_datetime = datetime.strptime(archive_date, archive_date_format)

# Create MoJGithub object
moj_gh = MojGithub (
    org=organization,
    org_token=org_token
)

# Get all repos that need archiving
repos = [repo for repo in moj_gh.get_unarchived_repos("public") if repo.pushed_at < archive_datetime]

# Print repos
for repo in repos:
    print(f"Repo: {repo.name}")
    print(f"Last pushed: {repo.pushed_at}")
    print("-----------------------------")
