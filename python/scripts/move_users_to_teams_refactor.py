import os
from dataclasses import dataclass, field

from python.services.github_service import GithubService
from python.config.constants import (
    MINISTRY_OF_JUSTICE,
    MOJ_ANALYTICAL_SERVICES
)

IGNORE_REPOSITORIES_AS_ORG = []
IGNORE_TEAMS_AS_ORG = []

IGNORE_REPOSITORIES_MOJ_ORG = []
IGNORE_TEAMS_MOJ_ORG = []


@dataclass
class RepositoryTeam:
    name: str = ""
    usernames: list = field(default_factory=list)
    permission_to_repository: str = ""
    id: int = 0


@dataclass
class Repository:
    name: str = ""
    issue_section_enabled: bool = False
    direct_users: list = field(default_factory=list)
    teams: list = field(default_factory=list)


def get_ignore_lists(organisation_name: str) -> tuple | ValueError:
    ignore_repositories = []
    ignore_teams = []

    if organisation_name == MINISTRY_OF_JUSTICE:
        ignore_repositories = [repo.lower() for repo in IGNORE_REPOSITORIES_MOJ_ORG]
        ignore_teams = [team.lower() for team in IGNORE_TEAMS_MOJ_ORG]
    elif organisation_name == MOJ_ANALYTICAL_SERVICES:
        ignore_repositories = [repo.lower() for repo in IGNORE_REPOSITORIES_AS_ORG]
        ignore_teams = [team.lower() for team in IGNORE_TEAMS_AS_ORG]
    else:
        raise ValueError(
            f"Unsupported Github Organisation Name [{organisation_name}]")

    return ignore_repositories, ignore_teams


def get_environment_variables() -> tuple:
    github_token = os.getenv("ADMIN_GITHUB_TOKEN")
    if not github_token:
        raise ValueError(
            "The env variable ADMIN_GITHUB_TOKEN is empty or missing")

    org_name = os.getenv("ORG_NAME")
    if not org_name:
        raise ValueError("The env variable ORG_NAME is empty or missing")

    return github_token, org_name


def get_repo_direct_access_users(github_service: GithubService, repository: dict, org_outside_collaborators: list) -> list:
    users_with_direct_access = []
    # Get repository users but exclude the outside collaborators
    if repository["number_of_direct_users"] > 0:
        users_with_direct_access = [
            user
            for user in github_service.get_repository_direct_users(repository["repository_name"])
            if user not in org_outside_collaborators
        ]
    return users_with_direct_access


def get_org_repositories(github_service: GithubService, ignore_repositories: list) -> list:
    return [
        repository
        for repository in github_service.get_repositories_info()
        if repository["repository_name"] not in ignore_repositories
    ]


def get_repository_teams(github_service: GithubService, repository_name: str, ignore_teams: list) -> list:
    return [
        RepositoryTeam(team)
        for team in github_service.get_repository_teams(repository_name)
        if team.name.lower() not in ignore_teams
    ]


def get_repositories_with_direct_users(github_service: GithubService) -> list[Repository]:
    repositories_with_direct_users = []
    ignore_repositories, ignore_teams = get_ignore_lists(org_name)
    org_outside_collaborators = github_service.get_outside_collaborators_login_names()
    for repository in get_org_repositories(github_service, ignore_repositories):
        users_with_direct_access = get_repo_direct_access_users(github_service, repository, org_outside_collaborators)
        repository_name = repository["repository_name"]
        if len(users_with_direct_access) > 0:
            repository_teams = get_repository_teams(github_service, repository_name, ignore_teams)
            repositories_with_direct_users.append(
                Repository(
                    repository_name,
                    repository["issue_section_enabled"],
                    users_with_direct_access,
                    repository_teams
                )
            )
    return repositories_with_direct_users


def get_ops_eng_team_usernames(github_service: GithubService):
    return github_service.get_a_team_usernames("operations-engineering")


def main():
    print("Start")
    github_token, org_name = get_environment_variables()
    github_service = GithubService(github_token, org_name)
    ops_eng_team_usernames = get_ops_eng_team_usernames(github_service)
    repositories_with_direct_users = get_repositories_with_direct_users(github_service)
    print("Finished")


if __name__ == "__main__":
    main()
