import os
from datetime import datetime
from dateutil.relativedelta import *
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

# How long ago in which the repositories should be archived
archive_date_days = 0
archive_date_months = 0
archive_date_years = 4

archive_date = datetime.now() - relativedelta(
    days=archive_date_days,
    months=archive_date_months,
    years=archive_date_years
)

# Create MoJGithub object
moj_gh = MojGithub (
    org=organization,
    org_token=org_token
)

# Get all repos that need archiving
repos = [repo for repo in moj_gh.get_unarchived_repos("public") if repo.pushed_at < archive_date]

# Print repos
print("-----------------------------")
print(f"Searching for inactive repositories from date: {archive_date}")
print("-----------------------------")

for repo in repos:
    print(f"Repo: {repo.name}")
    print(f"Last pushed: {repo.pushed_at}")
    print("-----------------------------")

