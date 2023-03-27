from python.services.github_service import GithubService


def fetch_repo_names_and_issue_section_enabled(github_service: GithubService) -> list:
    """Get organisation repository names and the repository issue section state
    Returns:
        list[tuples(str, bool)]: A list of tuples containing the organisation repository names and issue section state
    """
    has_next_page = True
    after_cursor = None
    repositories = []

    while has_next_page:
        data = github_service.get_paginated_list_of_repositories(after_cursor)

        if data["organization"]["repositories"]["edges"] is not None:
            for repository in data["organization"]["repositories"]["edges"]:
                # Skip locked repositories
                if not (
                    repository["node"]["isDisabled"]
                    or repository["node"]["isLocked"]
                    or repository["node"]["isArchived"]
                ):
                    repositories.append(
                        (
                            repository["node"]["name"],
                            repository["node"]["hasIssuesEnabled"],
                        )
                    )

        has_next_page = data["organization"]["repositories"]["pageInfo"]["hasNextPage"]
        after_cursor = data["organization"]["repositories"]["pageInfo"]["endCursor"]

    return repositories


def fetch_repository_users_usernames_and_permissions(
    github_service: GithubService, repository_name: str
) -> list:
    """Get the usernames of the users associated to a repository and their access permission
    Args:
        github_service (GithubService): GitHub API wrapper object
        repository_name (string): Name of repository
    Returns:
        list[tuples(str, str)]: A list of tuples containing the user username and access permission to the repository
    """
    has_next_page = True
    after_cursor = None
    users_usernames = []

    while has_next_page:
        data = github_service.get_paginated_list_of_user_names_and_permissions_with_direct_access_to_repository(
            repository_name, after_cursor
        )

        if data["repository"]["collaborators"]["edges"] is not None:
            for repository in data["repository"]["collaborators"]["edges"]:
                users_usernames.append(
                    (repository["node"]["login"], repository["permission"])
                )

        has_next_page = data["repository"]["collaborators"]["pageInfo"]["hasNextPage"]
        after_cursor = data["repository"]["collaborators"]["pageInfo"]["endCursor"]

    return users_usernames


def fetch_team_names(github_service: GithubService) -> list:
    """Get the name of the teams within the organisation
    Returns:
        list[string]: A list of the organisation team names
    """
    has_next_page = True
    after_cursor = None
    team_names = []

    while has_next_page:
        data = github_service.get_paginated_list_of_team_names(after_cursor)

        if data["organization"]["teams"]["edges"] is not None:
            for team in data["organization"]["teams"]["edges"]:
                team_names.append(team["node"]["slug"])

        has_next_page = data["organization"]["teams"]["pageInfo"]["hasNextPage"]
        after_cursor = data["organization"]["teams"]["pageInfo"]["endCursor"]

    return team_names


def fetch_team_users_usernames(github_service: GithubService, team_name: str) -> list:
    """Get the list of users usernames within an organisation team
    Returns:
        list[str]: A list of the team user usernames
    """
    has_next_page = True
    after_cursor = None
    user_usernames = []

    while has_next_page:
        data = github_service.get_paginated_list_of_team_user_names(
            team_name, after_cursor
        )

        if data["organization"]["team"]["members"]["edges"] is not None:
            for team in data["organization"]["team"]["members"]["edges"]:
                user_usernames.append(team["node"]["login"])

        has_next_page = data["organization"]["team"]["members"]["pageInfo"][
            "hasNextPage"
        ]
        after_cursor = data["organization"]["team"]["members"]["pageInfo"]["endCursor"]

    return user_usernames


def fetch_team_repositories_and_permissions(
    github_service: GithubService, team_name: str
) -> list:
    """Get the name of the repositories and access permissions to the repositories for a team
    Returns:
        list[tuples(str, str)]: A list of tuples containing the repository names and access permission to the repository
    """
    has_next_page = True
    after_cursor = None
    repositories = []

    while has_next_page:
        data = github_service.get_paginated_list_of_team_repositories_and_permissions_and_permissions(
            team_name, after_cursor
        )

        if data["organization"]["team"]["repositories"]["edges"] is not None:
            for repository in data["organization"]["team"]["repositories"]["edges"]:
                repositories.append(
                    (repository["node"]["name"], repository["permission"])
                )

        has_next_page = data["organization"]["team"]["repositories"]["pageInfo"][
            "hasNextPage"
        ]
        after_cursor = data["organization"]["team"]["repositories"]["pageInfo"][
            "endCursor"
        ]

    return repositories


# # todo
# def remove_users_with_duplicate_access(github_service: GithubService, repo_issues_enabled,
#                                        repository_name, repository_direct_users, org_teams
#                                        ):
#     """Check which users have access to the repository through a team
#     and direct access and remove their direct access permission, when
#     the team has the same or higher permissions than the user does.

#     Args:
#         github_service (GithubService): GitHub API wrapper object
#         repo_issues_enabled (bool): repo section enabled state on repository
#         repository_name (string): the name of the repository
#         repository_direct_users (list): the users that have a direct access to the repository
#         org_teams (list): a list of the organizations teams

#     Returns:
#         users_not_in_a_team (list): a list of the repository users with direct access
#     """
#     previous_user = ""
#     previous_repository = ""
#     users_not_in_a_team = repository_direct_users.copy()

#     # loop through each repository direct users
#     for username in repository_direct_users:
#         # loop through all the organisation teams
#         for team in org_teams:
#             # see if that team is attached to the repository and contains the direct user
#             if (repository_name in team.team_repositories) and (
#                 username in team.team_users
#             ):
#                 # This check helps skip duplicated results
#                 if (username != previous_user) and (
#                     repository_name != previous_repository
#                 ):
#                     # raise an issue to say the user has been removed and has access via the team
#                     if repo_issues_enabled.get(repository_name, repo_issues_enabled):
#                         github_service.create_an_access_removed_issue_for_user_in_repository(username,
#                                                                                              repository_name)

#                     # remove the direct user from the repository
#                     github_service.remove_user_from_repository(
#                         username, repository_name)

#                     # save values for next iteration
#                     previous_user = username
#                     previous_repository = repository_name

#                     # The user is in a team
#                     users_not_in_a_team.remove(username)
#     return users_not_in_a_team

# # todo
# def put_user_into_existing_team(
#     github_service: GithubService, repository_name, username, users_not_in_a_team, org_teams
# ):
#     """Put a user with direct access to a repository into an existing team

#     Args:
#         github_service (GithubService): GitHub API wrapper object
#         repository_name (string): the name of the repository
#         username (string): the name of the user
#         users_not_in_a_team (list): a list of the repositories users with direct access
#         org_teams (list): a list of the organizations teams
#     """

#     if repository_name == "" or username == "" or len(org_teams) == 0:
#         users_not_in_a_team.clear()
#     elif len(users_not_in_a_team) == 0:
#         pass
#     else:
#         users_permission = github_service.get_user_permission_for_repository(
#             username, repository_name)

#         # create a team name that has the same permissions as the user
#         temp_name = repository_name + "-" + users_permission + "-team"
#         expected_team_name = correct_team_name(temp_name)

#         # Find an existing team with the same permissions as
#         # the user which has access to the repository
#         for team in org_teams:
#             if (expected_team_name == team.name) and (
#                 repository_name in team.team_repositories
#             ):
#                 github_service.add_user_to_team(username, team.team_id)
#                 github_service.remove_user_from_repository(
#                     username, repository_name)
#                 users_not_in_a_team.remove(username)

# # todo
# def put_users_into_new_team(github_service: GithubService, repository_name, remaining_users):
#     """put users into a new team

#     Args:
#         github_service (GithubService): GitHub API wrapper object
#         repository_name (string): the name of the repository
#         remaining_users (list): a list of user names that have direct access to the repository
#     """
#     team_id = 0

#     if repository_name == "" or len(remaining_users) == 0:
#         return
#     else:
#         for username in remaining_users:
#             try:
#                 users_permission = github_service.get_user_permission_for_repository(
#                     username, repository_name)

#                 temp_name = repository_name + "-" + users_permission + "-team"
#                 team_name = correct_team_name(temp_name)

#                 if not github_service.team_exists(team_name):
#                     github_service.create_new_team_with_repository(
#                         team_name, repository_name)
#                     team_id = github_service.get_team_id_from_team_name(
#                         team_name)
#                     # Depends who adds the oauth_token to repo is added to every team
#                     github_service.remove_user_from_team(
#                         "AntonyBishop", team_id)
#                     github_service.remove_user_from_team("nickwalt01", team_id)
#                     github_service.remove_user_from_team("ben-al", team_id)
#                     github_service.remove_user_from_team(
#                         "moj-operations-engineering-bot", team_id)

#                 team_id = github_service.get_team_id_from_team_name(team_name)
#                 github_service.amend_team_permissions_for_repository(
#                     team_id, users_permission, repository_name)

#                 github_service.add_user_to_team(username, team_id)
#                 github_service.remove_user_from_repository(
#                     username, repository_name)
#             except Exception:
#                 logging.exception(
#                     f"Exception while putting {username} into team. Skipping iteration.")
