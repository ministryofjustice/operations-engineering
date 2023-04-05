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

        self.org_name = org_name
        self.github_service = github_service

        self.outside_collaborators = []
        self.repositories = []
        self.teams = []
        self.operations_engineering_team_user_usernames = []
        self.repositories_with_direct_users = []

    def setup(self):
        self.get_outside_collaborators()
        self.create_repositories()
        self.create_teams()
        self.get_ops_eng_team_user_usernames()
        self.add_teams_to_repositories()
        self.find_repositories_with_direct_users()
        self.add_ops_eng_team_to_repositories_with_direct_users()

    def get_outside_collaborators(self):
        return self.github_service.get_outside_collaborators_login_names()

    def create_repositories(self):
        for repository in self.helpers.fetch_repo_names_and_issue_section_enabled():
            self.repositories.append(
                Repository(
                    self.github_service,
                    repository[self.constants.username],
                    repository[self.constants.issue_section_enabled],
                    self.outside_collaborators,
                )
            )

        # Remove repository objects from the list that are in the badly_named_repositories list
        self.repositories[:] = [
            repository
            for repository in self.repositories
            if repository.name not in self.config.badly_named_repositories
        ]

    def create_teams(self):
        for team_name in self.helpers.fetch_team_names():
            self.teams.append(Team(self.helpers, team_name))

        # Remove teams that are in the ignore list
        for ignore_team_name in self.config.ignore_teams:
            self.teams[:] = [
                team for team in self.teams[:] if team.name != ignore_team_name
            ]

    def add_teams_to_repositories(self):
        for team in self.teams:
            for team_attached_to_repository in team.repositories_and_permissions:
                for repository in self.repositories:
                    if team_attached_to_repository[self.constants.repository_name] == repository.name:
                        repository.add_team(team)

    def get_ops_eng_team_user_usernames(self):
        for team in self.teams:
            if team.name == self.constants.operations_engineering_team_name:
                self.operations_engineering_team_user_usernames = team.users_usernames

    def find_repositories_with_direct_users(self):
        self.repositories_with_direct_users = [
            repository
            for repository in self.repositories
            if len(repository.direct_users_and_permission) > 0
        ]

    def add_ops_eng_team_to_repositories_with_direct_users(self):
        for repository in self.repositories_with_direct_users:
            repository.add_ops_eng_team_user_names(
                self.operations_engineering_team_user_usernames)

    def close_expired_issues(self):
        for repository in self.repositories:
            self.github_service.close_expired_issues(repository.name)

    def move_direct_users_to_teams(self):
        for repository in self.repositories_with_direct_users:
            repository.ensure_repository_teams_exists()
            repository.put_direct_users_into_teams()
            repository.create_repo_issues_for_direct_users()
            repository.remove_direct_users_access()
