import argparse
import logging
import sys

from services.GithubService import GithubService


def identify_support_issues(gh: GithubService, args):
    issues = gh.get_open_issues_from_repo(f"{args.org}/{args.repo}")

    return [
        issue
        for issue in issues
        for label in issue.labels
        if label.name == args.tag and len(issue.assignees) == 0
    ]


def assign_issues_to_creator(support_issues):
    for issue in support_issues:
        issue.edit(assignees=[issue.user.login])
        logging.info(f"Assigned issue {issue.number} to {issue.user.login}")


def add_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--oauth_token",
        type=str,
        required=True,
        help="The GitHub OAuth token to use",
    )

    parser.add_argument(
        "--org",
        type=str,
        default="ministryofjustice",
        help="The GitHub organisation to use",
    )

    parser.add_argument(
        "--repo",
        type=str,
        default="operations-engineering",
        help="The GitHub repository to use",
    )

    parser.add_argument(
        "--tag",
        type=str,
        default="Support",
        help="The GitHub tag to use",
    )

    return parser.parse_args()


def main():
    args = add_arguments()

    gh = GithubService(args.oauth_token, args.org)

    support_issues = identify_support_issues(gh, args)
    if not support_issues:
        logging.info("No support issues found")
        sys.exit(0)

    for issue in support_issues:
        print("Issue: ", issue.number, issue.title)

    try:
        assign_issues_to_creator(support_issues)
    except Exception:
        message = "Error: An exception occurred while assigning issues"
        logging.error(message, exc_info=True)


if __name__ == "__main__":
    main()
