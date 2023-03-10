import logging
import sys

from services.GithubService import GithubService


def identify_support_issues(issues, tag):
    return [
        issue
        for issue in issues
        for label in issue.labels
        if label.name == tag and len(issue.assignees) == 0
    ]


def assign_issues_to_creator(support_issues):
    for issue in support_issues:
        issue.edit(assignees=[issue.user.login])
        logging.info(f"Assigned issue {issue.number} to {issue.user.login}")


def main():
    if len(sys.argv) == 2:
        # Get the GH Action token
        oauth_token = sys.argv[1]
    else:
        raise ValueError("Missing a script input parameter")

    org = "ministryofjustice"
    repo = "operations-engineering"
    tag = "Support"

    gh = GithubService(oauth_token, org)

    issues = gh.get_open_issues_from_repo(repo)
    if not issues:
        logging.info("No open issues found")
        sys.exit(0)

    support_issues = identify_support_issues(issues, tag)
    if not support_issues:
        logging.info("No support issues found")
        sys.exit(0)

    try:
        assign_issues_to_creator(support_issues)
    except Exception:
        message = "Warning: Exception in Run()"
        logging.error(message, exc_info=True)


if __name__ == "__main__":
    main()
