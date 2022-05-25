import sys
import traceback
import time
from datetime import datetime
from datetime import timedelta
from github import Github
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport

# Get the GH Action token
oauth_token = sys.argv[1]

repo_issues_enabled = {}
outside_collaborators = []

MINISTRYOFJUSTICE = "ministryofjustice/"


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


# Setup a transport and client to interact with the GH GraphQL API
try:
    transport = AIOHTTPTransport(
        url="https://api.github.com/graphql",
        headers={"Authorization": "Bearer {}".format(oauth_token)},
    )
except Exception:
    print_stack_trace("Exception: Problem with the API URL or GH Token")

try:
    client = Client(transport=transport, fetch_schema_from_transport=False)
except Exception:
    print_stack_trace("Exception: Problem with the Client.")


def repository_user_names_query(after_cursor=None, repository_name=None) -> gql:
    """A GraphQL query to get the list of user names within a repository that have direct access.

    Args:
        after_cursor (string, optional): Is the pagination offset value gathered from the previous API request. Defaults to None.
        repository_name (string, optional): Is the name of the repository that has the associated user/s. Defaults to None.

    Returns:
        gql: The GraphQL query result
    """
    query = """
    query {
        repository(name: REPOSITORY_NAME, owner: "ministryofjustice") {
            collaborators(first: 100, after:AFTER, affiliation: DIRECT) {
                edges {
                    node {
                        login
                    }
                }
                pageInfo {
                    hasNextPage
                    endCursor
                }
            }
        }
    }
    """.replace(
        # This is the next page ID to start the fetch from
        "AFTER",
        '"{}"'.format(after_cursor) if after_cursor else "null",
    ).replace(
        "REPOSITORY_NAME",
        '"{}"'.format(repository_name) if repository_name else "null",
    )

    return gql(query)


def organisation_repo_name_query(after_cursor=None) -> gql:
    """A GraphQL query to get the list of organisation repo names

    Args:
        after_cursor (string, optional): Is the pagination offset value gathered from the previous API request. Defaults to None.

    Returns:
        gql: The GraphQL query result
    """
    query = """
    query {
        organization(login: "ministryofjustice") {
            repositories(first: 100, after:AFTER) {
                pageInfo {
                    endCursor
                    hasNextPage
                }
                edges {
                    node {
                        name
                        isDisabled
                        isArchived
                        isLocked
                        hasIssuesEnabled
                    }
                }
            }
        }
    }
        """.replace(
        # This is the next page ID to start the fetch from
        "AFTER",
        '"{}"'.format(after_cursor) if after_cursor else "null",
    )

    return gql(query)


def organisation_teams_name_query(after_cursor=None) -> gql:
    """A GraphQL query to get the list of organisation team names

    Args:
        after_cursor (string, optional): Is the pagination offset value gathered from the previous API request. Defaults to None.

    Returns:
        gql: The GraphQL query result
    """
    query = """
    query {
        organization(login: "ministryofjustice") {
            teams(first: 100, after:AFTER) {
                pageInfo {
                    endCursor
                    hasNextPage
                }
                edges {
                    node {
                        slug
                    }
                }
            }
        }
    }
        """.replace(
        # This is the next page ID to start the fetch from
        "AFTER",
        '"{}"'.format(after_cursor) if after_cursor else "null",
    )

    return gql(query)


def organisation_team_id_query(team_name=None) -> gql:
    """A GraphQL query to get the id of an organisation team

    Args:
        team_name (string, optional): Name of the organisation team. Defaults to None.

    Returns:
        gql: The GraphQL query result
    """
    query = """
    query {
        organization(login: "ministryofjustice") {
            team(slug: TEAM_NAME) {
                databaseId
            }
        }
    }
        """.replace(
        # This is the team name
        "TEAM_NAME",
        '"{}"'.format(team_name) if team_name else "null",
    )

    return gql(query)


def team_repos_query(after_cursor=None, team_name=None) -> gql:
    """A GraphQL query to get the list of repos a team has access to in the organisation

    Args:
        after_cursor (string, optional): Is the pagination offset value gathered from the previous API request. Defaults to None.
        team_name (string, optional): Is the name of the team that has the associated repo/s. Defaults to None.

    Returns:
        gql: The GraphQL query result
    """
    query = """
    query {
        organization(login: "ministryofjustice") {
            team(slug: TEAM_NAME) {
                repositories(first: 100, after:AFTER) {
                    edges {
                        node {
                            name
                        }
                    }
                    pageInfo {
                        endCursor
                        hasNextPage
                    }
                }
            }
        }
    }
    """.replace(
        # This is the next page ID to start the fetch from
        "AFTER",
        '"{}"'.format(after_cursor) if after_cursor else "null",
    ).replace(
        "TEAM_NAME",
        '"{}"'.format(team_name) if team_name else "null",
    )

    return gql(query)


def team_user_names_query(after_cursor=None, team_name=None) -> gql:
    """A GraphQL query to get the list of user names within each organisation team.

    Args:
        after_cursor (string, optional): Is the pagination offset value gathered from the previous API request. Defaults to None.
        team_name (string, optional): Is the name of the team that has the associated user/s. Defaults to None.

    Returns:
        gql: The GraphQL query result
    """
    query = """
    query {
        organization(login: "ministryofjustice") {
            team(slug: TEAM_NAME) {
                members(first: 100, after:AFTER) {
                    edges {
                        node {
                            login
                        }
                    }
                    pageInfo {
                        hasNextPage
                        endCursor
                    }
                }
            }
        }
    }
    """.replace(
        # This is the next page ID to start the fetch from
        "AFTER",
        '"{}"'.format(after_cursor) if after_cursor else "null",
    ).replace(
        "TEAM_NAME",
        '"{}"'.format(team_name) if team_name else "null",
    )

    return gql(query)


def fetch_repo_names() -> list:
    """A wrapper function to run a GraphQL query to get the list of repo names in the organisation

    Returns:
        list: A list of the organisation repos names
    """
    has_next_page = True
    after_cursor = None
    repo_name_list = []

    while has_next_page:
        query = organisation_repo_name_query(after_cursor)
        data = client.execute(query)

        # Retrieve the name of the repos
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


def fetch_repository_users(repository_name) -> list:
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
        query = repository_user_names_query(after_cursor, repository_name)
        data = client.execute(query)

        # Retrieve the usernames of the repository members
        for repository in data["repository"]["collaborators"]["edges"]:
            # Ignore users that are outside collaborators
            global outside_collaborators
            if repository["node"]["login"] not in outside_collaborators:
                repository_user_name_list.append(repository["node"]["login"])

        # Read the GH API page info section to see if there is more data to read
        has_next_page = data["repository"]["collaborators"]["pageInfo"]["hasNextPage"]
        after_cursor = data["repository"]["collaborators"]["pageInfo"]["endCursor"]

    return repository_user_name_list


def fetch_team_names() -> list:
    """A wrapper function to run a GraphQL query to get the list of teams in the organisation

    Returns:
        list: A list of the organisation team names
    """
    has_next_page = True
    after_cursor = None
    team_name_list = []

    while has_next_page:
        query = organisation_teams_name_query(after_cursor)
        data = client.execute(query)

        # Retrieve the name of the teams
        for team in data["organization"]["teams"]["edges"]:
            team_name_list.append(team["node"]["slug"])

        # Read the GH API page info section to see if there is more data to read
        has_next_page = data["organization"]["teams"]["pageInfo"]["hasNextPage"]
        after_cursor = data["organization"]["teams"]["pageInfo"]["endCursor"]

    return team_name_list


def fetch_team_id(team_name) -> int:
    """A wrapper function to run a GraphQL query to get the team ID

    Args:
        team_name (string): The team name

    Returns:
        int: The team ID of the team
    """
    query = organisation_team_id_query(team_name)
    data = client.execute(query)
    if data["organization"]["team"]["databaseId"]:
        return data["organization"]["team"]["databaseId"]
    else:
        return 0


def fetch_team_users(team_name) -> list:
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
        query = team_user_names_query(after_cursor, team_name)
        data = client.execute(query)

        # Retrieve the usernames of the team members
        for team in data["organization"]["team"]["members"]["edges"]:
            team_user_name_list.append(team["node"]["login"])

        # Read the GH API page info section to see if there is more data to read
        has_next_page = data["organization"]["team"]["members"]["pageInfo"][
            "hasNextPage"
        ]
        after_cursor = data["organization"]["team"]["members"]["pageInfo"]["endCursor"]

    return team_user_name_list


def fetch_team_repos(team_name) -> list:
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
        query = team_repos_query(after_cursor, team_name)
        data = client.execute(query)

        # Retrieve the name of the teams repos
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


class repository:
    """A struct to store repository info ie name and users"""

    name: str
    direct_members: list

    def __init__(self, x, y):
        self.name = x
        self.direct_members = y


def fetch_repository(repository_name) -> repository:
    """Fetches the repository info from GH

    Args:
        repository_name (string): Name of the repository

    Returns:
        repository: A repository object
    """
    repository_users_list = fetch_repository_users(repository_name)
    return repository(repository_name, repository_users_list)


def fetch_repositories() -> list:
    """Wrapper function to retrieve the repositories info ie name, users

    Returns:
        list: A list that contains all the repositories data ie name, users
    """
    repositories_list = []
    repository_names_list = fetch_repo_names()
    for repository_name in repository_names_list:
        repositories_list.append(fetch_repository(repository_name))

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


def fetch_team(team_name) -> team:
    """Fetches the team info from GH

    Args:
        team_name (string): Name of the team

    Returns:
        team: A team object
    """
    team_users_list = fetch_team_users(team_name)
    team_repos_list = fetch_team_repos(team_name)
    team_id = fetch_team_id(team_name)
    return team(team_name, team_users_list, team_repos_list, team_id)


def fetch_teams() -> list:
    """Wrapper function to retrieve the organisation team info ie name, users, repos

    Returns:
        list: A list that contains all the organisation teams data ie name, users, repos
    """
    teams_list = []
    teams_names_list = fetch_team_names()
    for team_name in teams_names_list:
        teams_list.append(fetch_team(team_name))

    return teams_list


def remove_user_from_repository(user_name, repository_name):
    """Removes the user from the repository

    Args:
        user_name (string): User name of the user to remove
        repository_name (string): Name of repository
    """
    # Delay for GH API
    time.sleep(10)

    try:
        gh = Github(oauth_token)
        repo = gh.get_repo(MINISTRYOFJUSTICE + repository_name)
        repo.remove_from_collaborators(user_name)
        print(
            "Removing the user "
            + user_name
            + " from the repository: "
            + repository_name
        )
    except Exception:
        message = (
            "Warning: Exception in removing a user "
            + user_name
            + " from the repository: "
            + repository_name
        )
        print_stack_trace(message)


def create_an_issue(user_name, repository_name):
    """Create an issue for the user in the repository

    Args:
        user_name (string): The username of the user
        repository_name (string): The name of the repository
    """

    if repo_issues_enabled.get(repository_name):
        # Delay for GH API
        time.sleep(10)

        try:
            gh = Github(oauth_token)
            repo = gh.get_repo(MINISTRYOFJUSTICE + repository_name)
            repo.create_issue(
                title="User access removed, access is now via a team",
                body="Hi there \n\n The user "
                + user_name
                + " had Direct Member access to this repository and access via a team. \n\n Access is now only via a team. \n\n You may have less access it is dependant upon the teams access to the repo. \n\n If you have any questions, please post in #ask-operations-engineering on Slack. \n\n This issue can be closed. ",
                assignee=user_name,
            )
        except Exception:
            message = (
                "Warning: Exception in creating an issue for user "
                + user_name
                + " in the repository: "
                + repository_name
            )
            print_stack_trace(message)


def close_expired_issues(repository_name):
    """Close issues that have been open longer than 45 days

    Args:
        repository_name (string): The name of the repository
    """

    try:
        gh = Github(oauth_token)
        repo = gh.get_repo(MINISTRYOFJUSTICE + repository_name)
        issues = repo.get_issues()
        for issue in issues:
            # Check for open issues that match the issue created by this script
            if (
                issue.title == "User access removed, access is now via a team"
                and issue.state == "open"
            ):
                created_date = issue.created_at
                grace_period = created_date + timedelta(days=45)
                # Check if the 45 day grace period has expired
                if grace_period < datetime.now():
                    # Close issue
                    issue.edit(state="closed")

                    # Delay for GH API
                    time.sleep(10)
    except Exception:
        message = (
            "Warning: Exception in closing issue in the repository: " + repository_name
        )
        print_stack_trace(message)


def get_outside_collaborators():
    """
    Create a list of the outside collaborators usernames

    Returns:
        list: The list of outside collaborators usernames
    """
    usernames = []
    try:
        gh = Github(oauth_token)
        org = gh.get_organization("ministryofjustice")
        for outside_collaborator in org.get_outside_collaborators():
            usernames.append(outside_collaborator.login)
    except Exception:
        message = "Warning: Exception in getting outside collaborators in get_outside_collaborators()"
        print_stack_trace(message)

    return usernames


def remove_users_with_duplicate_access(
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
                    create_an_issue(username, repository_name)

                    # remove the direct user from the repository
                    remove_user_from_repository(username, repository_name)

                    # save values for next iteration
                    previous_user = username
                    previous_repository = repository_name

                    # The user is in a team
                    users_not_in_a_team.remove(username)


def get_user_permission(repository_name, username):
    """gets the user permissions for a repository

    Args:
        repository_name (string): the name of the repository
        username (string): the name of the user

    Returns:
        string: the user permission level
    """
    users_permission = None

    try:
        gh = Github(oauth_token)
        repo = gh.get_repo(MINISTRYOFJUSTICE + repository_name)
        user = gh.get_user(username)
        users_permission = repo.get_collaborator_permission(user)
    except Exception:
        message = "Warning: Exception getting the users permission " + username
        print_stack_trace(message)

    return users_permission


def remove_user_from_team(team_id, username):
    """remove a user from a team

    Args:
        team_id (int): the GH ID of the team
        username (string): the name of the user
    """
    try:
        gh = Github(oauth_token)
        org = gh.get_organization("ministryofjustice")
        gh_team = org.get_team(team_id)
        user = gh.get_user(username)
        gh_team.remove_membership(user)
        print("Remove user " + username + " from team " + team_id.__str__())
    except Exception:
        message = (
            "Warning: Exception in removing user "
            + username
            + " from team "
            + team_id.__str__()
        )
        print_stack_trace(message)


def add_user_to_team(team_id, username):
    """add a user to a team

    Args:
        team_id (int): the GH ID of the team
        username (string): the name of the user
    """
    try:
        gh = Github(oauth_token)
        org = gh.get_organization("ministryofjustice")
        gh_team = org.get_team(team_id)
        user = gh.get_user(username)
        gh_team.add_membership(user)
        print("Add user " + username + " to team " + team_id.__str__())
    except Exception:
        message = (
            "Warning: Exception in adding user "
            + username
            + " to team "
            + team_id.__str__()
        )
        print_stack_trace(message)


def create_new_team_with_repository(repository_name, team_name):
    """create a new team and attach to a repository

    Args:
        repository_name (string): the name of the repository to attach to
        team_name (string): the name of the team
    """
    try:
        gh = Github(oauth_token)
        repo = gh.get_repo(MINISTRYOFJUSTICE + repository_name)
        org = gh.get_organization("ministryofjustice")
        org.create_team(
            team_name,
            [repo],
            "",
            "closed",
            "Automated generated team to grant users access to this repository",
        )
    except Exception:
        message = "Warning: Exception in creating a team " + team_name
        print_stack_trace(message)


def does_team_exist(team_name):
    """Check if a team exists in the organization

    Args:
        team_name (string): the name of the team

    Returns:
        bool: if the team was found in the organization
    """

    team_found = False

    try:
        gh = Github(oauth_token)
        org = gh.get_organization("ministryofjustice")
        gh_teams = org.get_teams()
        for gh_team in gh_teams:
            if gh_team.name == team_name:
                team_found = True
                break
    except Exception:
        message = "Warning: Exception in check to see if a team exists " + team_name
        print_stack_trace(message)

    return team_found


def change_team_repository_permission(repository_name, team_name, team_id, permission):
    """changes the team permissions on a repository

    Args:
        repository_name (string): the name of the repository
        team_name (string): the name of the team
        team_id (int): the GH id of the team
        permission (string): the permission of the team
    """
    if permission == "read":
        permission = "pull"
    elif permission == "write":
        permission = "push"

    try:
        gh = Github(oauth_token)
        repo = gh.get_repo(MINISTRYOFJUSTICE + repository_name)
        org = gh.get_organization("ministryofjustice")
        gh_team = org.get_team(team_id)
        gh_team.update_team_repository(repo, permission)
    except Exception:
        message = (
            "Warning: Exception in changing team "
            + team_name
            + " permission on repository "
            + repository_name
        )
        print_stack_trace(message)


def put_user_into_existing_team(
    repository_name, username, users_not_in_a_team, org_teams
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
        return
    elif len(users_not_in_a_team) == 0:
        return
    else:
        users_permission = get_user_permission(repository_name, username)

        # create a team name that has the same permissions as the user
        expected_team_name = repository_name + "-" + users_permission + "-team"

        # Find an existing team with the same permissions as
        # the user which has access to the repository
        for team in org_teams:
            if (expected_team_name == team.name) and (
                repository_name in team.team_repositories
            ):
                add_user_to_team(team.team_id, username)
                remove_user_from_repository(username, repository_name)
                users_not_in_a_team.remove(username)


def put_users_into_new_team(repository_name, remaining_users):
    """put users into a new team

    Args:
        repository_name (string): the name of the repository
        remaining_users (list): a list of user names that have direct access to the repository
    """
    team_created = False
    team_id = 0

    if repository_name == "" or len(remaining_users) == 0:
        return
    else:
        for username in remaining_users:
            users_permission = get_user_permission(repository_name, username)

            team_name = repository_name + "-" + users_permission + "-team"

            if not does_team_exist(team_name):
                create_new_team_with_repository(repository_name, team_name)
                team_created = True

            team_id = fetch_team_id(team_name)

            change_team_repository_permission(
                repository_name, team_name, team_id, users_permission
            )

            add_user_to_team(team_id, username)
            remove_user_from_repository(username, repository_name)

        if team_created:
            remove_user_from_team(team_id, "AntonyBishop")


def run():
    """A function for the main functionality of the script"""

    # Get the usernames of the outside collaborators
    global outside_collaborators
    outside_collaborators = get_outside_collaborators()

    # Get the MoJ organisation teams and users info
    org_teams = fetch_teams()

    # Get the MoJ organisation repos and direct users
    org_repositories = fetch_repositories()

    # loop through each organisation repository
    for repository in org_repositories:

        # close any previously opened issues that have expired
        close_expired_issues(repository.name)

        users_not_in_a_team = repository.direct_members

        remove_users_with_duplicate_access(
            repository.name, repository.direct_members, users_not_in_a_team, org_teams
        )

        remaining_users = users_not_in_a_team

        for username in users_not_in_a_team:
            put_user_into_existing_team(
                repository.name, username, remaining_users, org_teams
            )

        put_users_into_new_team(repository.name, remaining_users)


print("Start")
run()
print("Finished")
sys.exit(0)
