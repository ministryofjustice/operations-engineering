import argparse
import logging

from python.services.github_service import GithubService
from python.services.operations_engineering_reports import OperationsEngineeringReportsService
from python.services.standards_service import RepositoryReport


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
        "--url",
        type=str,
        required=True,
        help="The operations-engineering-reports url to use with the leading https:// and without the trailing /",
    )

    parser.add_argument(
        "--endpoint",
        type=str,
        required=True,
        help="The operations-engineering-reports endpoint to use without the leading /",
    )

    parser.add_argument(
        "--api-key",
        type=str,
        required=True,
        help="The API key to use for the operations-engineering-reports endpoint",
    )

    parser.add_argument(
        "--enc-key",
        type=str,
        required=True,
        help="The encryption key to use for the operations-engineering-reports endpoint",
    )

    return parser.parse_args()


def parse_args(args):
    if args.url[-1] == "/":
        args.url = args.url[:-1]

    if args.endpoint[0] == "/":
        args.endpoint = args.endpoint[1:]

    if args.enc_key[:2] == "0x":
        args.enc_key = args.enc_key[2:]

    return args


def main():
    # Add arguments from the command line
    args = parse_args(add_arguments())

    # Fetch all repositories in the org
    repos = GithubService(
        args.oauth_token, args.org).fetch_all_repositories_in_org()

    # Generate GitHub standards report for each repository in the org
    repo_reports = [RepositoryReport(repo).output for repo in repos]

    # Send the reports to the operations-engineering-reports API
    try:
        OperationsEngineeringReportsService(args.url, args.endpoint, args.api_key, args.enc_key)\
            .override_repository_standards_reports(repo_reports)
    except AssertionError as error:
        logging.error(
            f" A failure occurred communicating with {args.url}/{args.endpoint}: {error}")


if __name__ == "__main__":
    main()
