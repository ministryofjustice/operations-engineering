import logging
import sys
import traceback

from services.GithubService import GithubService


def print_stack_trace(message):
    """Print a stack trace when an exception occurs

    Args:
        message (string): A message to print when exception occurs
    """
    print(message)
    try:
        exc_info = sys.exc_info()
    finally:
        traceback.print_exception(*exc_info)
        del exc_info


def fetch_repo_names(github_service: GithubService, repo_issues_enabled) -> list:
    """A wrapper function to run a GraphQL query to get the list of repo names in the organisation

    Returns:
        list: A list of the organisation repos names
    """
    has_next_page = True
    after_cursor = None
    repo_name_list = []

    while has_next_page:
        data = github_service.get_paginated_list_of_repositories(after_cursor)

        # Retrieve the name of the repos
        if data["organization"]["repositories"]["edges"] is not None:
            for repo in data["organization"]["repositories"]["edges"]:
                # Skip locked repositories
                if not (
                    repo["node"]["isDisabled"]
                    or repo["node"]["isArchived"]
                    or repo["node"]["isLocked"]
                ):
                    repo_name_list.append(repo["node"]["name"])
                    repo_issues_enabled[repo["node"]["name"]] = repo["node"][
                        "hasIssuesEnabled"
                    ]

        # Read the GH API page info section to see if there is more data to read
        has_next_page = data["organization"]["repositories"]["pageInfo"]["hasNextPage"]
        after_cursor = data["organization"]["repositories"]["pageInfo"]["endCursor"]

    return repo_name_list


def fetch_repository_users(github_service: GithubService, repository_name: str,
                           outside_collaborators: list[str]) -> list:
    """A wrapper function to run a GraphQL query to get the list of users within an repository with direct access

    Args:
        repository_name (string): Is the repository within the organisation to check

    Returns:
        list: A list of the repository user names
    """
    has_next_page = True
    after_cursor = None
    repository_user_name_list = []

    while has_next_page:
        data = github_service.get_paginated_list_of_user_names_with_direct_access_to_repository(repository_name,
                                                                                                after_cursor)

        # Retrieve the usernames of the repository members
        if data["repository"]["collaborators"]["edges"] is not None:
            for repository in data["repository"]["collaborators"]["edges"]:
                # Ignore users that are outside collaborators
                if repository["node"]["login"] not in outside_collaborators:
                    repository_user_name_list.append(
                        repository["node"]["login"])

        # Read the GH API page info section to see if there is more data to read
        has_next_page = data["repository"]["collaborators"]["pageInfo"]["hasNextPage"]
        after_cursor = data["repository"]["collaborators"]["pageInfo"]["endCursor"]

    return repository_user_name_list


def fetch_team_names(github_service: GithubService) -> list:
    """A wrapper function to run a GraphQL query to get the list of teams in the organisation

    Returns:
        list: A list of the organisation team names
    """
    has_next_page = True
    after_cursor = None
    team_name_list = []

    while has_next_page:
        data = github_service.get_paginated_list_of_team_names(after_cursor)

        # Retrieve the name of the teams
        if data["organization"]["teams"]["edges"] is not None:
            for team in data["organization"]["teams"]["edges"]:
                team_name_list.append(team["node"]["slug"])

        # Read the GH API page info section to see if there is more data to read
        has_next_page = data["organization"]["teams"]["pageInfo"]["hasNextPage"]
        after_cursor = data["organization"]["teams"]["pageInfo"]["endCursor"]

    return team_name_list


def fetch_team_users(github_service: GithubService, team_name) -> list:
    """A wrapper function to run a GraphQL query to get the list of users within an organisation team

    Args:
        team_name (string): Is the team within the organisation to check

    Returns:
        list: A list of the team user names
    """
    has_next_page = True
    after_cursor = None
    team_user_name_list = []

    while has_next_page:
        data = github_service.get_paginated_list_of_team_user_names(
            team_name, after_cursor)

        # Retrieve the usernames of the team members
        if data["organization"]["team"]["members"]["edges"] is not None:
            for team in data["organization"]["team"]["members"]["edges"]:
                team_user_name_list.append(team["node"]["login"])

        # Read the GH API page info section to see if there is more data to read
        has_next_page = data["organization"]["team"]["members"]["pageInfo"][
            "hasNextPage"
        ]
        after_cursor = data["organization"]["team"]["members"]["pageInfo"]["endCursor"]

    return team_user_name_list


def fetch_team_repos(github_service: GithubService, team_name) -> list:
    """A wrapper function to run a GraphQL query to get the list of repo within in an organisation team

    Args:
        team_name (string): Is the team within the organisation to check

    Returns:
        list: A list of team repo names
    """
    has_next_page = True
    after_cursor = None
    team_repo_list = []

    while has_next_page:
        data = github_service.get_paginated_list_of_team_repositories(
            team_name, after_cursor)

        # Retrieve the name of the teams repos
        if data["organization"]["team"]["repositories"]["edges"] is not None:
            for team in data["organization"]["team"]["repositories"]["edges"]:
                team_repo_list.append(team["node"]["name"])

        # Read the GH API page info section to see if there is more data to read
        has_next_page = data["organization"]["team"]["repositories"]["pageInfo"][
            "hasNextPage"
        ]
        after_cursor = data["organization"]["team"]["repositories"]["pageInfo"][
            "endCursor"
        ]

    return team_repo_list


class Repository:
    """A struct to store repository info ie name and users"""

    name: str
    direct_members: list

    def __init__(self, x, y):
        self.name = x
        self.direct_members = y


def fetch_repository(github_service: GithubService, repository_name, outside_collaborators: list[str]) -> Repository:
    """Fetches the repository info from GH

    Args:
        repository_name (string): Name of the repository

    Returns:
        Repository: A repository object
    """
    repository_users_list = fetch_repository_users(
        github_service, repository_name, outside_collaborators)
    return Repository(repository_name, repository_users_list)


def fetch_repositories(github_service: GithubService, outside_collaborators: list[str], repo_issues_enabled) -> list:
    """Wrapper function to retrieve the repositories info ie name, users

    Returns:
        list: A list that contains all the repositories data ie name, users
    """
    repositories_list = []
    repository_names_list = fetch_repo_names(
        github_service, repo_issues_enabled)
    for repository_name in repository_names_list:
        repositories_list.append(fetch_repository(
            github_service, repository_name, outside_collaborators))

    return repositories_list


class team:
    """A struct to store team info ie name, users, repos, GH ID"""

    name: str
    team_users: list
    team_repositories: list
    team_id: int

    def __init__(self, a, b, c, d):
        self.name = a
        self.team_users = b
        self.team_repositories = c
        self.team_id = d


def fetch_team(github_service: GithubService, team_name) -> team:
    """Fetches the team info from GH

    Args:
        team_name (string): Name of the team

    Returns:
        team: A team object
    """
    team_users_list = fetch_team_users(github_service, team_name)
    team_repos_list = fetch_team_repos(github_service, team_name)
    team_id = github_service.get_team_id_from_team_name(team_name)
    return team(team_name, team_users_list, team_repos_list, team_id)


def fetch_teams(github_service: GithubService) -> list:
    """Wrapper function to retrieve the organisation team info ie name, users, repos

    Returns:
        list: A list that contains all the organisation teams data ie name, users, repos
    """
    teams_list = []
    teams_names_list = fetch_team_names(github_service)
    for team_name in teams_names_list:
        try:
            teams_list.append(fetch_team(github_service, team_name))
        except Exception:
            logging.exception(
                f"Exception fetching team name {team_name} information. Skipping iteration.")

    return teams_list


def remove_users_with_duplicate_access(github_service: GithubService, repo_issues_enabled,
                                       repository_name, repository_direct_users, users_not_in_a_team, org_teams
                                       ):
    """Check which users have access to the repo through a team
    and direct access and remove their direct access permission.

    Args:
        repository_name (string): the name of the repository
        repository_direct_users (list): user names of the repositories users
        users_not_in_a_team (list): a duplicate list of the repositories users
        org_teams (list): a list of the organizations teams
    """
    previous_user = ""
    previous_repository = ""

    # loop through each repository direct users
    for username in repository_direct_users:
        # loop through all the organisation teams
        for team in org_teams:
            # see if that team is attached to the repository and contains the direct user
            if (repository_name in team.team_repositories) and (
                username in team.team_users
            ):
                # This check helps skip duplicated results
                if (username != previous_user) and (
                    repository_name != previous_repository
                ):
                    # raise an issue to say the user has been removed and has access via the team
                    if repo_issues_enabled.get(repository_name, repo_issues_enabled):
                        github_service.create_an_access_removed_issue_for_user_in_repository(username,
                                                                                             repository_name)

                    # remove the direct user from the repository
                    github_service.remove_user_from_repository(
                        username, repository_name)

                    # save values for next iteration
                    previous_user = username
                    previous_repository = repository_name

                    # The user is in a team
                    users_not_in_a_team.remove(username)


def correct_team_name(team_name):
    """GH team names use a slug name. This
    swaps ., _, , with a - and lower cases
    the team name

    Args:
        team_name (string): the name of the team

    Returns:
        string: converted team name
    """
    temp_name = ""
    new_team_name = ""

    temp_name = team_name
    temp_name = temp_name.replace(".", "-")
    temp_name = temp_name.replace("_", "-")
    temp_name = temp_name.replace(" ", "-")
    temp_name = temp_name.replace("---", "-")
    temp_name = temp_name.replace("--", "-")

    if temp_name.startswith(".") or temp_name.startswith("-"):
        temp_name = temp_name[1:]

    if temp_name.endswith(".") or temp_name.endswith("-"):
        temp_name = temp_name[:-1]

    new_team_name = temp_name.lower()

    return new_team_name


def put_user_into_existing_team(
    github_service: GithubService, repository_name, username, users_not_in_a_team, org_teams
):
    """Put a user with direct access to a repository into an existing team

    Args:
        repository_name (string): the name of the repository
        username (string): the name of the user
        users_not_in_a_team (list): a list of the repositories users with direct access
        org_teams (list): a list of the organizations teams
    """

    if repository_name == "" or username == "" or len(org_teams) == 0:
        users_not_in_a_team.clear()
    elif len(users_not_in_a_team) == 0:
        pass
    else:
        users_permission = github_service.get_user_permission_for_repository(
            username, repository_name)

        # create a team name that has the same permissions as the user
        temp_name = repository_name + "-" + users_permission + "-team"
        expected_team_name = correct_team_name(temp_name)

        # Find an existing team with the same permissions as
        # the user which has access to the repository
        for team in org_teams:
            if (expected_team_name == team.name) and (
                repository_name in team.team_repositories
            ):
                github_service.add_user_to_team(username, team.team_id)
                github_service.remove_user_from_repository(
                    username, repository_name)
                users_not_in_a_team.remove(username)


def put_users_into_new_team(github_service: GithubService, repository_name, remaining_users):
    """put users into a new team

    Args:
        repository_name (string): the name of the repository
        remaining_users (list): a list of user names that have direct access to the repository
    """
    team_id = 0

    if repository_name == "" or len(remaining_users) == 0:
        return
    else:
        for username in remaining_users:
            try:
                users_permission = github_service.get_user_permission_for_repository(
                    username, repository_name)

                temp_name = repository_name + "-" + users_permission + "-team"
                team_name = correct_team_name(temp_name)


                if not github_service.team_exists(team_name):
                    github_service.create_new_team_with_repository(
                        team_name, repository_name)
                    team_id = github_service.get_team_id_from_team_name(team_name)
                    # Depends who adds the oauth_token to repo is added to every team
                    github_service.remove_user_from_team(
                        "AntonyBishop", team_id)
                    github_service.remove_user_from_team("nickwalt01", team_id)
                    github_service.remove_user_from_team("ben-al", team_id)
                    github_service.remove_user_from_team(
                        "moj-operations-engineering-bot", team_id)

                team_id = github_service.get_team_id_from_team_name(team_name)
                github_service.amend_team_permissions_for_repository(
                    team_id, users_permission, repository_name)

                github_service.add_user_to_team(username, team_id)
                github_service.remove_user_from_repository(
                    username, repository_name)
            except Exception:
                logging.exception(
                    f"Exception while putting {username} into team. Skipping iteration.")


def run(github_service: GithubService, badly_named_repositories: list[str], repo_issues_enabled):
    """A function for the main functionality of the script"""

    # Get the usernames of the outside collaborators
    outside_collaborators = github_service.get_outside_collaborators_login_names()

    # Get the MoJ organisation teams and users info
    org_teams = fetch_teams(github_service)

    # Get the MoJ organisation repos and direct users
    org_repositories = fetch_repositories(
        github_service, outside_collaborators, repo_issues_enabled)

    # loop through each organisation repository
    for repository in org_repositories:

        if repository.name not in badly_named_repositories:
            # close any previously opened issues that have expired
            github_service.close_expired_issues(repository.name)

            users_not_in_a_team = repository.direct_members

            remove_users_with_duplicate_access(github_service, repo_issues_enabled,
                                               repository.name,
                                               repository.direct_members,
                                               users_not_in_a_team,
                                               org_teams,
                                               )

            remaining_users = users_not_in_a_team

            for username in users_not_in_a_team:
                put_user_into_existing_team(github_service,
                                            repository.name, username, remaining_users, org_teams
                                            )

            put_users_into_new_team(
                github_service, repository.name, remaining_users)


def main():
    if len(sys.argv) == 2:
        oauth_token = sys.argv[1]
    else:
        raise ValueError("Missing a script input parameter")
    github_service = GithubService(oauth_token, "ministryofjustice")
    repo_issues_enabled = {}
    badly_named_repositories = [
        "https---github.com-ministryofjustice-hmpps-incentives-tool",
    ]
    print("Start")
    run(github_service, badly_named_repositories, repo_issues_enabled)
    print("Finished")


if __name__ == "__main__":
    main()
