import argparse

from python.lib.repository_standards import RepositoryStandards
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

    return parser.parse_args()


def main():
    # Accept token as an argument
    # Generate new GitHub Token
    args = add_arguments()

    repos = GithubService(args.oauth_token, args.org).fetch_all_repositories_in_org()

    for repo in repos:
        standards = RepositoryStandards(repo)
        print(standards.report())
        print("-----")
        if standards.is_compliant() is False:
            print(standards.compliance_report())
        break


if __name__ == "__main__":
    main()
