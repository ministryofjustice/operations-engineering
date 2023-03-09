import os
import sys

from github import Github
from services.GithubService import GithubService

# This file assigns unassigned support tickets to the user that opened the ticket
# Its goal is to streamline the capture of support tickets as far as possible

# Config

# Create Base Objects
# Authentication, Repository, Issues
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


def main():
    if len(sys.argv) == 2:
        # Get the GH Action token
        oauth_token = sys.argv[1]
    else:
        raise ValueError("Missing a script input parameter")

    org = "ministryofjustice"
    repo = "operations-engineering"
    tag = "Support"

    github_service = GithubService(oauth_token, org)
    # Concept
    # Get a list of repos
    # repos = github_service.get_repos()
    #
    # # Get a list of issues
    # issues = github_service.get_issues(repo, tag)
    #
    # # Get a list of unassigned issues
    # unassigned_issues = github_service.get_unassigned_issues(repo, tag)
    #
    # # Assign issues to the creator
    # github_service.assign_issues_to_creator(repo, tag)
    #
    # # Print the results
    # print(f"Repos: {repos}")
    # print(f"Issues: {issues}")
    # print(f"Unassigned Issues: {unassigned_issues}")
