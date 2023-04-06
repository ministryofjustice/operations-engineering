import logging

from python.services.github_service import GithubService
from python.lib.constants import Constants
from python.lib.config import Config
from python.lib.repository import Repository
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

        self.outside_collaborators = self.github_service.get_outside_collaborators_login_names()
        self.repositories = []
        self.repositories_with_direct_users = []
        self.ops_eng_team_user_usernames = self.github_service.get_a_team_user_usernames(
            self.constants.operations_engineering_team_name)
        self.__fetch_repositories()
        self.__create_repositories_with_direct_users()

    def __fetch_repositories(self):
        self.repositories = [
            repository
            for repository in self.helpers.fetch_repo_names_and_issue_section_enabled()
            # ignore repositories in the badly_named_repositories list
            if repository[self.constants.username].lower() not in self.config.badly_named_repositories
        ]

    def __create_repositories_with_direct_users(self):
        for repository in self.repositories:
            direct_users = self.github_service.get_repository_direct_users(
                repository[self.constants.username])

            if len(direct_users) > 0:
                direct_users[:] = [
                    user
                    for user in direct_users
                    if user not in self.outside_collaborators
                ]

                if len(direct_users) > 0:
                    # if direct_users.totalCount != 0:
                    self.repositories_with_direct_users.append(
                        Repository(
                            self.github_service,
                            repository[self.constants.username].lower(),
                            repository[self.constants.issue_section_enabled],
                            direct_users,
                            self.ops_eng_team_user_usernames
                        )
                    )

    def close_expired_issues(self):
        for repository in self.repositories:
            self.github_service.close_expired_issues(
                repository[self.constants.username].lower())

    def move_direct_users_to_teams(self):
        for repository in self.repositories_with_direct_users:
            repository.get_existing_teams()
            repository.ensure_repository_teams_exists()
            repository.put_direct_users_into_teams()
            repository.create_repo_issues_for_direct_users()
            repository.remove_direct_users_access()
