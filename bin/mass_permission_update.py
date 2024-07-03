import argparse
import json
import os
import logging
from typing import List, Dict
from services.github_service import GithubService


def read_repository_list(file_path: str) -> List[Dict[str, str]]:
    try:
        with open(file=file_path, mode='r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        logging.error("Repository list file not found: %s", file_path)
        raise
    except json.JSONDecodeError:
        logging.error("Invalid JSON in repository list file: %s", file_path)
        raise


def get_environment_variables() -> tuple:
    org_token = os.getenv('GITHUB_TOKEN')
    if not org_token:
        raise ValueError(
            "The env variable GITHUB_TOKEN is empty or missing")
    org_name = os.getenv("GITHUB_ORG_NAME") or 'ministryofjustice'

    return org_token, org_name


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Update GitHub team repository permissions.")
    parser.add_argument(
        "team_name", help="The name of the GitHub team that needs the permission change.")
    parser.add_argument(
        "permission_level", help="The permission level to set for the team (e.g., admin, write, read).")
    return parser.parse_args()


def main():
    args = parse_arguments()

    org_token, org_name = get_environment_variables()

    github_service = GithubService(org_token, org_name)
    repositories = read_repository_list('repositories.json')
    github_service.update_team_repository_permission(args.team_name, repositories, args.permission_level)

    logging.info("Script has completed successfully.")


if __name__ == "__main__":
    main()
