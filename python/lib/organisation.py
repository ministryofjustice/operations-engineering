import logging

from python.services.github_service import GithubService
from python.lib.constants import Constants
from python.lib.config import Config
from python.lib.repository import Repository
from python.lib.team import Team
from python.lib.helpers import Helpers


class Organisation:
    """The Organisation info contains the repositories, collaborators and teams"""

    # Added to fix error in command: python3 -m unittest discover python/test -v
    def __new__(cls, *_, **__):
        return super(Organisation, cls).__new__(cls)

    def __init__(self, github_service: GithubService, org_name: str):
        self.constants = Constants()
        self.config = Config()
        self.helpers = Helpers(github_service)

        self.org_name = org_name.lower()
        self.github_service = github_service

        self.outside_collaborators = []
        self.repositories = []
        self.teams = []
        self.ops_eng_team_user_usernames = []
        self.repositories_with_direct_users = []

    def setup(self):
        self.get_outside_collaborators()
        self.create_teams()
        self.get_ops_eng_team_user_usernames()
        self.fetch_repositories()
        self.create_repositories_with_direct_users()
        self.add_teams_to_repositories_with_direct_users()

    def get_outside_collaborators(self):
        self.outside_collaborators = [
            username.lower()
            for username in self.github_service.get_outside_collaborators_login_names()
        ]

    def create_teams(self):
        self.teams = [
            Team(self.helpers, team_name.lower())
            for team_name in self.helpers.fetch_team_names()
            # ignore teams in the ignore list
            if team_name.lower() not in self.config.ignore_teams
        ]

    def get_ops_eng_team_user_usernames(self):
        self.ops_eng_team_user_usernames = [
            team
            for team in self.teams
            if team.name.lower() == self.constants.operations_engineering_team_name.lower()
        ]

    def fetch_repositories(self):
        self.repositories = [
            repository
            for repository in self.helpers.fetch_repo_names_and_issue_section_enabled()
            # ignore repositories in the badly_named_repositories list
            if repository[self.constants.username].lower() not in self.config.badly_named_repositories
        ]

    def get_users_with_direct_access_to_repository(self, repository_name):
        return [
            (user_username.lower(), self.github_service.get_user_permission_for_repository(
                user_username.lower(), repository_name))
            for user_username in self.helpers.fetch_repository_users_with_direct_access_to_repository(repository_name)
            if user_username not in self.outside_collaborators
        ]

    def create_repositories_with_direct_users(self):
        for repository in self.repositories:
            direct_users_and_permission = self.get_users_with_direct_access_to_repository(
                repository[self.constants.username])
            if len(direct_users_and_permission) > 0:
                self.repositories_with_direct_users.append(
                    Repository(
                        self.github_service,
                        repository[self.constants.username].lower(),
                        repository[self.constants.issue_section_enabled],
                        direct_users_and_permission,
                        self.ops_eng_team_user_usernames
                    )
                )

    def add_teams_to_repositories_with_direct_users(self):
        for repository in self.repositories_with_direct_users:
            teams = [
                team
                for team in self.teams
                for team_attached_to_repository in team.repositories_and_permissions
                if team_attached_to_repository[self.constants.repository_name].lower() == repository.name.lower()
            ]
            repository.add_teams(teams)

    def close_expired_issues(self):
        for repository in self.repositories:
            self.github_service.close_expired_issues(
                repository[self.constants.username].lower())

    def move_direct_users_to_teams(self):
        for repository in self.repositories_with_direct_users:
            repository.ensure_repository_teams_exists()
            repository.put_direct_users_into_teams()
            repository.create_repo_issues_for_direct_users()
            repository.remove_direct_users_access()
