import argparse

from services.github_service import GithubService
from config.logging_config import logging


def add_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--oauth-token",
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

    try:
        issues = gh.assign_support_issues_to_self(
            args.repo, args.org, args.tag)
    except ValueError as error:
        logging.error(f"Failed to assign issues: {error}")
        raise error

    if not issues:
        logging.warning("No issues found, skipping")
    for issue in issues:
        logging.info(
            f"Assigned issue {issue.number} to {issue.assignees}")


if __name__ == "__main__":
    main()
