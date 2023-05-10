import argparse

from python.lib.repository_standards import RepositoryReport, OrganisationStandardsReport
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
        "--endpoint",
        type=str,
        required=True,
        help="The operations-engineering-reports endpoint to use",
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


def main():
    # Add arguments from the command line
    args = add_arguments()

    # Fetch all repositories in the org
    repos = GithubService(args.oauth_token, args.org).fetch_all_repositories_in_org()

    # Create a report that will be sent to the API
    report = OrganisationStandardsReport(
        args.endpoint, args.api_key, args.enc_key
    )

    # Add each repository to the report and post
    [report.add(RepositoryReport(repo)) for repo in repos]
    try:
        report.send_to_api()
    except ValueError:
        print("Failed to send report to API")


if __name__ == "__main__":
    main()
