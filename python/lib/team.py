from python.services.github_service import GithubService
from python.lib.helpers import Helpers


class Team:
    """A struct to store team info ie name, users, repos, GH ID"""

    def __init__(self, github_service: GithubService, name: str):
        self.github_service = github_service
        self.helper = Helpers(github_service)
        self.name = name
        self.users_usernames = self.helper.fetch_team_users_usernames(
            self.name)
        self.repositories_and_permissions = self.helper.fetch_team_repositories_and_permissions(
            self.name)
        self.id = self.github_service.get_team_id_from_team_name(self.name)

    def add_new_team_repository_permission(repository_name: str, repository_permission: str):
        self.repositories_and_permissions.append(
            (repository_name, repository_permission))

    def add_new_team_user(user_username: str):
        self.users_usernames.append(user_username)
