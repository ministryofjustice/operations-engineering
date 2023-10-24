import os
from dataclasses import dataclass, field

from services.github_service import GithubService
from config.constants import (
    MINISTRY_OF_JUSTICE,
    MOJ_ANALYTICAL_SERVICES
)

IGNORE_REPOSITORIES_AS_ORG = []
IGNORE_TEAMS_AS_ORG = []

IGNORE_REPOSITORIES_MOJ_ORG = []
IGNORE_TEAMS_MOJ_ORG = [
    "organisation-security-auditor"
]


@dataclass
class RepositoryTeam:
    name: str = ""
    users: list = field(default_factory=list)
    permission: str = ""
    id: int = 0


@dataclass
class Repository:
    name: str = ""
    issue_section_enabled: bool = False
    direct_users: list = field(default_factory=list)
    teams: list = field(default_factory=list)


def get_ignore_teams_list(organisation_name: str) -> tuple | ValueError:
    ignore_teams = []

    if organisation_name == MINISTRY_OF_JUSTICE:
        ignore_teams = [team.lower() for team in IGNORE_TEAMS_MOJ_ORG]
    elif organisation_name == MOJ_ANALYTICAL_SERVICES:
        ignore_teams = [team.lower() for team in IGNORE_TEAMS_AS_ORG]
    else:
        raise ValueError(
            f"Unsupported Github Organisation Name [{organisation_name}]")

    return ignore_teams


def get_ignore_repositories_list(organisation_name: str) -> tuple | ValueError:
    ignore_repositories = []

    if organisation_name == MINISTRY_OF_JUSTICE:
        ignore_repositories = [repo.lower()
                               for repo in IGNORE_REPOSITORIES_MOJ_ORG]
    elif organisation_name == MOJ_ANALYTICAL_SERVICES:
        ignore_repositories = [repo.lower()
                               for repo in IGNORE_REPOSITORIES_AS_ORG]
    else:
        raise ValueError(
            f"Unsupported Github Organisation Name [{organisation_name}]")

    return ignore_repositories


def get_environment_variables() -> tuple:
    github_token = os.getenv("ADMIN_GITHUB_TOKEN")
    if not github_token:
        raise ValueError(
            "The env variable ADMIN_GITHUB_TOKEN is empty or missing")

    org_name = os.getenv("ORG_NAME")
    if not org_name:
        raise ValueError("The env variable ORG_NAME is empty or missing")

    return github_token, org_name


def get_repository_users(github_service: GithubService, repository_name: str, org_outside_collaborators: list) -> list:
    # Get repository users but exclude the outside collaborators
    return [
        user
        for user in github_service.get_repository_direct_users(repository_name)
        if user not in org_outside_collaborators
    ]


def get_repository_org_users(github_service: GithubService, repository: dict, org_outside_collaborators: list) -> list:
    repository_users = []
    if repository["collaborators"]["totalCount"] > 0:
        repository_users = get_repository_users(
            github_service, repository["name"], org_outside_collaborators)
    return repository_users


def get_org_repositories(github_service: GithubService) -> list:
    ignore_repositories = get_ignore_repositories_list(
        github_service.organisation_name)
    return [
        repository
        for repository in github_service.fetch_all_repositories_in_org()
        if repository["name"] not in ignore_repositories
    ]


def get_repository_teams(github_service: GithubService, repository_name: str) -> list:
    repository_teams = []
    ignore_teams = get_ignore_teams_list(github_service.organisation_name)
    gh_repository_teams = [
        team
        for team in github_service.get_repository_teams(repository_name)
        if team.slug.lower() not in ignore_teams
    ]
    for gh_repository_team in gh_repository_teams:
        team_users = [
            user.login.lower()
            for user in gh_repository_team.get_members()
        ]
        repository_teams.append(
            RepositoryTeam(
                gh_repository_team.slug.lower(),
                team_users,
                gh_repository_team.permission,
                gh_repository_team.id
            )
        )
    return repository_teams


def get_repositories_with_direct_users(github_service: GithubService, org_outside_collaborators: list) -> list[Repository]:
    repositories_with_direct_users = []
    for repository in get_org_repositories(github_service):
        users = get_repository_org_users(
            github_service, repository, org_outside_collaborators)
        if len(users) > 0:
            repository_teams = get_repository_teams(
                github_service, repository["name"])
            repositories_with_direct_users.append(
                Repository(
                    repository["name"],
                    repository["hasIssuesEnabled"],
                    users,
                    repository_teams
                )
            )
    return repositories_with_direct_users


def does_user_have_team_access(github_service: GithubService, repository: Repository, user: str):
    has_team_access = False
    user_repository_permission = github_service.get_user_permission_for_repository(
        user, repository.name)
    for repository_team in repository.teams:
        if user in repository_team.users and user_repository_permission == repository_team.permission:
            has_team_access = True
            break
    return has_team_access


def remove_repository_users_with_team_access(github_service: GithubService, repositories: list):
    for repository in repositories:
        for user in repository.direct_users:
            if does_user_have_team_access(github_service, repository, user):
                raise_issue_on_repository(
                    github_service, repository.name, repository.issue_section_enabled, user)
                github_service.remove_user_from_repository(
                    user, repository.name)


def put_users_into_repository_teams(github_service: GithubService, users: list, repository_name: str):
    repository_teams = get_repository_teams(github_service, repository_name)
    for user in users:
        user_repository_permission = github_service.get_user_permission_for_repository(
            user, repository_name)
        team_name = form_team_name(user_repository_permission, repository_name)
        for repository_team in repository_teams:
            if repository_team.name == team_name:
                if len(repository_team.users) == 0 or user_repository_permission == "admin":
                    github_service.add_user_to_team_as_maintainer(
                        user, repository_team.id)
                else:
                    github_service.add_user_to_team(user, repository_team.id)
                break


def form_team_name(users_permission: str, repository_name: str) -> str:
    """ GH team names use a slug name. This swaps ., _, , with
        a - and then lower cases the team name
    """
    temp_name = repository_name + "-" + users_permission + "-team"
    temp_name = temp_name.replace(".", "-")
    temp_name = temp_name.replace("_", "-")
    temp_name = temp_name.replace(" ", "-")
    temp_name = temp_name.replace("---", "-")
    temp_name = temp_name.replace("--", "-")
    temp_name = temp_name.replace("--", "-")

    if temp_name.startswith(".") or temp_name.startswith("-"):
        temp_name = temp_name[1:]

    return temp_name.lower()


def is_new_team_needed(expected_team_name: str, teams: list) -> bool:
    new_team_required = True
    for team in teams:
        if team.name.lower() == expected_team_name.lower():
            new_team_required = False
            break
    return new_team_required


def create_a_team_on_github(github_service: GithubService, team_name: str, repository_name: str) -> int:
    team_id = 0
    if not github_service.team_exists(team_name):
        github_service.create_new_team_with_repository(
            team_name, repository_name)
        team_id = github_service.get_team_id_from_team_name(team_name)
    return team_id


def remove_operations_engineering_team_users_from_team(github_service: GithubService, team_id: int):
    """ When team is created GH adds the user who ran the GH action to the team
        this function removes the user from that team
    """
    for user in github_service.get_a_team_usernames("operations-engineering"):
        github_service.remove_user_from_team(user, team_id)


def ensure_repository_teams_exists(github_service: GithubService, users: list, repository_name: str, teams: list):
    """ Check if a automated team with the required permission already
        exists. If not create a new repository team with required permission.
    """
    for user in users:
        user_repository_permission = github_service.get_user_permission_for_repository(
            user, repository_name)
        expected_team_name = form_team_name(
            user_repository_permission, repository_name)
        if is_new_team_needed(expected_team_name, teams):
            team_id = create_a_team_on_github(
                github_service, expected_team_name, repository_name)
            if team_id > 0:
                github_service.amend_team_permissions_for_repository(
                    team_id, user_repository_permission, repository_name)
                remove_operations_engineering_team_users_from_team(
                    github_service, team_id)


def raise_issue_on_repository(github_service: GithubService, repository_name: str, is_repo_issue_section_enabled: bool, user: str):
    if is_repo_issue_section_enabled:
        github_service.create_an_access_removed_issue_for_user_in_repository(
            user, repository_name)


def move_remaining_repository_users_into_teams(github_service: GithubService, repositories: list, org_outside_collaborators: list):
    for repository in repositories:
        users = get_repository_users(
            github_service, repository.name, org_outside_collaborators)
        if len(users) > 0:
            ensure_repository_teams_exists(
                github_service, users, repository.name, repository.teams)
            put_users_into_repository_teams(
                github_service, users, repository.name)
            for user in users:
                raise_issue_on_repository(
                    github_service, repository.name, repository.issue_section_enabled, user)
                github_service.remove_user_from_repository(
                    user, repository.name)


def main():
    print("Start")
    github_token, org_name = get_environment_variables()
    github_service = GithubService(github_token, org_name)
    org_outside_collaborators = github_service.get_outside_collaborators_login_names()
    repositories = get_repositories_with_direct_users(
        github_service, org_outside_collaborators)
    remove_repository_users_with_team_access(github_service, repositories)
    move_remaining_repository_users_into_teams(
        github_service, repositories, org_outside_collaborators)
    print("Finished")


if __name__ == "__main__":
    main()
