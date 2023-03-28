import logging

from python.services.github_service import GithubService
from python.lib.constants import Constants
from python.lib.config import Config
from python.lib.repository import Repository
from python.lib.team import Team
from python.lib import helpers


logger = logging.getLogger(__name__)


class Organisation:
    """The Organisation info contains the repositories, collaborators and teams"""

    # Added to fix error in command: python3 -m unittest discover python/test -v
    def __new__(cls, *_, **__):
        return super(Organisation, cls).__new__(cls)

    def __init__(self, github_service, org_name: str):
        self.constants = Constants()
        self.config = Config()
        self.const_issue_section_enabled = self.constants.issue_section_enabled
        self.const_name = self.constants.name

        self.org_name = org_name
        self.github_service = github_service

        self.__outside_collaborators = (
            self.github_service.get_outside_collaborators_login_names()
        )

        # Create repository objects
        self.__repositories = []
        for repository in helpers.fetch_repo_names_and_issue_section_enabled(
            self.github_service
        ):
            self.__repositories.append(
                Repository(
                    self.github_service,
                    repository[self.const_name],
                    repository[self.const_issue_section_enabled],
                    self.__outside_collaborators,
                )
            )

        # Remove repository objects from the list that are in the badly_named_repositories list
        const_badly_named_repositories = self.config.get_badly_named_repositories()
        self.__repositories[:] = [
            repository
            for repository in self.__repositories
            if repository.name not in const_badly_named_repositories
        ]

        # Create team objects
        self.__teams = []
        for team_name in helpers.fetch_team_names(self.github_service):
            try:
                self.__teams.append(Team(self.github_service, team_name))
            except Exception:
                logging.exception(
                    f"Exception fetching team name {team_name} information. Skipping iteration."
                )

        # Remove teams that are in the ignore list
        for ignore_team_name in self.config.get_ignore_teams():
            self.__teams[:] = [
                team for team in self.__teams[:] if team.name != ignore_team_name
            ]

        # Add team objects to the repository objects where an association exists
        for team in self.__teams:
            for team_attached_repository in team.repositories_and_permissions:
                for repository in self.__repositories:
                    if team_attached_repository[self.const_name] == repository.name:
                        repository.add_team(team)

    @property
    def outside_collaborators(self):
        return self.__outside_collaborators

    @property
    def repositories(self):
        return self.__repositories

    @property
    def teams(self):
        return self.__teams

    def close_expired_issues(self):
        """Close any previously opened issues that have expired"""
        for repository in self.repositories:
            self.github_service.close_expired_issues(repository.name)

    def check_users_access(self):
        """tbc"""
        for repository in self.repositories:
            if len(repository.direct_users) > 0:
                repository.remove_direct_users()
