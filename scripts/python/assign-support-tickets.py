from github import Github
import os

# This file assigns unassigned support tickets to the user that opened the ticket
# Its goal is to streamline the capture of support tickets as far as possible

# Config
organization = "ministryofjustice"
repository = "operations-engineering"
project = f"{organization}/{repository}"
support_tag = "Support"

# Create Base Objects
# Authentication, Repository, Issues
git = Github(os.getenv("ADMIN_GITHUB_TOKEN"))
repo = git.get_repo(project)
issues = repo.get_issues(state="open")

# Get only unassigned support issues
support_issues = [
    issue
    for issue in issues
    for label in issue.labels
    if label.name == support_tag and len(issue.assignees) == 0
]

# Assign creator to item
for issue in support_issues:
    issue.edit(assignees=[issue.user.login])
