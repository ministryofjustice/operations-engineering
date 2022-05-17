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
            if (
                repo["node"]["isDisabled"]
                or repo["node"]["isArchived"]
                or repo["node"]["isLocked"]
            ):
                pass
            else:
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
    """A struct to store team info ie name, users, repos"""

    name: str
    team_users: list
    team_repositories: list

    def __init__(self, x, y, z):
        self.name = x
        self.team_users = y
        self.team_repositories = z


def fetch_team(team_name) -> team:
    """Fetches the team info from GH

    Args:
        team_name (string): Name of the team

    Returns:
        team: A team object
    """
    team_users_list = fetch_team_users(team_name)
    team_repos_list = fetch_team_repos(team_name)
    return team(team_name, team_users_list, team_repos_list)


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
        repo = gh.get_repo("ministryofjustice/" + repository_name)
        repo.remove_from_collaborators(user_name)
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
            repo = gh.get_repo("ministryofjustice/" + repository_name)
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
        repo = gh.get_repo("ministryofjustice/" + repository_name)
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
                    time.sleep(5)
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
    gh = Github(oauth_token)
    org = gh.get_organization("ministryofjustice")
    usernames = []
    for outside_collaborator in org.get_outside_collaborators():
        usernames.append(outside_collaborator.login)
    return usernames


def run():
    """A function for the main functionality of the script"""

    # Get the usernames of the outside collaborators
    outside_collaborators = get_outside_collaborators()

    # Get the MoJ organisation teams and users info
    org_teams = fetch_teams()

    # Get the MoJ organisation repos and direct users
    org_repositories = fetch_repositories()

    previous_direct_member = ""
    previous_repository_name = ""

    # loop through each organisation repository
    for repository in org_repositories:
        # close any previously opened issues that have expired
        close_expired_issues(repository.name)
        if repository.direct_members:
            print("\n" + repository.name)
        # loop through each repository direct members
        for direct_member in repository.direct_members:
            # Skip outside collaborators
            if direct_member not in outside_collaborators:
                print(direct_member)
                # loop through all the organisation teams
                for team in org_teams:
                    # see if that team is attached to the repository and contains the direct member
                    if (repository.name in team.team_repositories) and (
                        direct_member in team.team_users
                    ):
                        # This check helps skip duplicated results
                        if (direct_member == previous_direct_member) and (
                            repository.name == previous_repository_name
                        ):
                            pass
                        else:
                            # raise an issue to say the user has been removed and has access via the team
                            create_an_issue(direct_member, repository.name)

                            # remove the direct member from the repository
                            remove_user_from_repository(direct_member, repository.name)

                            print(
                                "Removing the user "
                                + direct_member
                                + " from the repository: "
                                + repository.name
                            )

                            # save values for next iteration
                            previous_direct_member = direct_member
                            previous_repository_name = repository.name


print("Start")
run()
print("Finished")
sys.exit(0)
