from github import Github
import os


def main():
    # This file closes any open support tickets as we are testing limited capture of support activities
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
