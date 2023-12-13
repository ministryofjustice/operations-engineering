import argparse
import json, os
from services.github_service import GithubService

def read_repository_list(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def main():
    
    parser = argparse.ArgumentParser(description="Update GitHub team repository permissions.")
    parser.add_argument("team_name", help="The name of the GitHub team that needs the permission change.")
    parser.add_argument("permission_level", help="The permission level to set for the team (e.g., admin, write, read).")
    args = parser.parse_args()
    
    org_token = os.getenv('GITHUB_TOKEN')

    if not org_token:
        raise ValueError("GitHub token not found. Make sure you have set it in your environment variables.")

    github_service = GithubService(org_token, "ministryofjustice")
    
    repositories = read_repository_list('repositories.json')

    github_service.update_team_repository_permission(args.team_name, repositories, args.permission_level)
    
    print("Script has completed.")

if __name__ == "__main__":
    main()