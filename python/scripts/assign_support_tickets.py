import argparse
import logging

from python.services.github_service import GithubService


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
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-8s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    gh = GithubService(args.oauth_token, args.org)
    issues = gh.assign_support_issues_to_self(args.repo, args.org, args.tag)
    if not issues:
        logging.warning("No issues found, skipping")
    for issue in issues:
        logging.info(f"Assigned issue {issue.number} to {issue.assignee.login}")


if __name__ == "__main__":
    main()
