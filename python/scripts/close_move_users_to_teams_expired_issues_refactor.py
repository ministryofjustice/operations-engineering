from python.scripts.move_users_to_teams_refactor import (
    get_environment_variables,
    get_org_repositories
)
from python.services.github_service import GithubService


def close_expired_issues(github_service: GithubService, org_name: str):
    for repository in get_org_repositories(github_service, org_name):
        github_service.close_expired_issues(repository[repository_name])


def main():
    print("Start")
    github_token, org_name = get_environment_variables()
    github_service = GithubService(github_token, org_name)
    close_expired_issues(github_service, org_name)
    print("Finished")

if __name__ == "__main__":
    main()
