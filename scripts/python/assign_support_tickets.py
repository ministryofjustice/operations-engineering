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
    logging.debug(f"Assigning {len(support_issues)} issues to their creator")

    for issue in support_issues:
        logging.debug(
            f"Issue number {issue.number}, created by {issue.user.login}")
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

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging",
    )

    return parser.parse_args()


def setup_logging(debug):
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)


def main():
    args = add_arguments()
    setup_logging(args.debug)

    logging.debug(f"args passed to the command line: {args}")

    gh = GithubService(args.oauth_token, args.org)

    support_issues = identify_support_issues(gh, args)
    logging.debug(f"support_issues identified: {support_issues}")
    if not support_issues:
        logging.info("No support issues found")
        sys.exit(0)

    try:
        assign_issues_to_creator(support_issues)
    except Exception:
        message = "Error: An exception occurred while assigning issues"
        logging.error(message, exc_info=True)


if __name__ == "__main__":
    main()
