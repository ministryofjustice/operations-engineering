import argparse

from python.lib.repository_standards import OrganisationStandardsReport, RepositoryReport
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

    repo_types = ["public", "private"]
    for repo_type in repo_types:
        report = OrganisationStandardsReport(
            args.endpoint, args.api_key, args.enc_key, repo_type)
        repo_reports = [RepositoryReport(repo) for repo in repos if RepositoryReport(repo).repository_type == repo_type]
        report.add(repo_reports)
        try:
            report.send_to_api()
        except ValueError:
            print(f"Error sending {repo_type} report to site")


if __name__ == "__main__":
    main()
