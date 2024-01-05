import argparse
import logging

from services.github_service import GithubService
from services.operations_engineering_reports import \
    OperationsEngineeringReportsService as reports_service
from services.standards_service import RepositoryReport


def __add_arguments():
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

    return parser.parse_args()


def __parse_args(args):
    if args.url[-1] == "/":
        args.url = args.url[:-1]

    if args.endpoint[0] == "/":
        args.endpoint = args.endpoint[1:]

    return args


def main():
    args = __parse_args(__add_arguments())
    repos = GithubService(
        args.oauth_token, args.org).fetch_all_repositories_in_org()
    repo_reports = [RepositoryReport(repo).output for repo in repos]
    reports_service(args.url, args.endpoint, args.api_key). \
        override_repository_standards_reports(repo_reports)


if __name__ == "__main__":
    main()
