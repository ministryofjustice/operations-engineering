import os
from github import Github


def main():
    # This file closes any open support tickets as we are testing limited capture of support activities
    # Its goal is to streamline the capture of support tickets as far as possible

    org_token = os.getenv("ADMIN_GITHUB_TOKEN")
    if not org_token:
        raise ValueError(
            "The env variable ADMIN_GITHUB_TOKEN is empty or missing")

    # Config
    organization = "ministryofjustice"
    repository = "operations-engineering"
    project = f"{organization}/{repository}"
    support_tag = "Support"

    # Create Base Objects
    # Authentication, Repository, Issues
    git = Github(org_token)
    repo = git.get_repo(project)
    issues = repo.get_issues(state="open")

    # Get only open support issues
    support_issues = [
        issue
        for issue in issues
        for label in issue.labels
        if label.name == support_tag and issue.state == "open"
    ]

    # Assign creator to item
    for issue in support_issues:
        issue.edit(state="closed")


if __name__ == "__main__":
    main()
