import os
import logging
from pyaml_env import parse_config

from python.services.github_service import GithubService
from python.lib.repository import Repository


class Organisation:
    """The Organisation info contains the repositories, collaborators and teams"""

    # Added this function to fix error in command: python3 -m unittest discover python/test -v
    def __new__(cls, *_, **__):
        return super(Organisation, cls).__new__(cls)

    def __init__(self, github_service: GithubService, org_name: str):
        self.repository_name = 0
        self.issue_section_enabled = 1
        self.number_of_direct_users = 2

        self.ignore_teams = []
        self.badly_named_repositories = []
        self.__load_config()

        self.org_name = org_name.lower()
        self.github_service = github_service

        self.outside_collaborators = self.github_service.get_outside_collaborators_login_names()

        self.ops_eng_team_user_usernames = self.github_service.get_a_team_usernames(
            "operations-engineering")

        # A list of tuples containing pre info for the repository objects
        self.repositories = []
        self.__fetch_repositories()

        # A list of repository objects
        self.repositories_with_direct_users = []
        self.__create_repositories_with_direct_users()

    def __load_config(self):
        config_file = os.getenv("CONFIG_FILE")
        if not config_file:
            raise ValueError(
                "The env variable CONFIG_FILE is empty or missing"
            )

        config_file_path = f"{os.path.dirname(os.path.realpath(__file__))}/../{config_file}"
        if not os.path.exists(config_file_path):
            raise ValueError(
                "Cannot find the config file"
            )

        configs = parse_config(config_file_path)

        if configs["badly_named_repositories"] is not None:
            self.badly_named_repositories = [
                repo_name.lower()
                for repo_name in configs["badly_named_repositories"]
            ]

        if configs["ignore_teams"] is not None:
            self.ignore_teams = [
                team_name.lower()
                for team_name in configs["ignore_teams"]
            ]

    def __fetch_repositories(self):
        self.repositories = [
            repository
            for repository in self.__fetch_repository_info()
            # ignore repositories in the badly_named_repositories list
            if repository[self.repository_name].lower() not in self.badly_named_repositories
        ]

    def __create_repositories_with_direct_users(self):
        for repository in self.repositories:
            users_with_direct_access = self.__fetch_users_with_direct_access(
                repository)
            if len(users_with_direct_access) > 0:
                self.repositories_with_direct_users.append(
                    Repository(
                        self.github_service,
                        repository[self.repository_name].lower(),
                        repository[self.issue_section_enabled],
                        users_with_direct_access,
                        self.ops_eng_team_user_usernames,
                        self.ignore_teams
                    )
                )

    def __fetch_users_with_direct_access(self, repository: tuple):
        users_with_direct_access = []

        if repository[self.number_of_direct_users] > 0:
            # Remove users who are outside collaborators
            users_with_direct_access = [
                user
                for user in self.github_service.get_repository_direct_users(repository[self.repository_name])
                if user not in self.outside_collaborators
            ]

        return users_with_direct_access

    def __fetch_repository_info(self) -> list[tuple]:
        repositories = []

        for repo_type in ["public", "private", "internal"]:
            after_cursor = None
            has_next_page = True
            while has_next_page:
                data = self.github_service.get_paginated_list_of_repositories_per_type(
                    repo_type, after_cursor)

                for repository in data["search"]["repos"]:
                    if not (
                        repository["repo"]["isDisabled"]
                        or repository["repo"]["isLocked"]
                    ):
                        repositories.append(
                            (
                                repository["repo"]["name"].lower(),
                                repository["repo"]["hasIssuesEnabled"],
                                repository["repo"]["collaborators"]["totalCount"],
                            )
                        )

                has_next_page = data["search"]["pageInfo"]["hasNextPage"]
                after_cursor = data["search"]["pageInfo"]["endCursor"]

        return repositories

    def close_expired_issues(self):
        for repository in self.repositories:
            self.github_service.close_expired_issues(
                repository[self.repository_name].lower())

    def move_users_to_teams(self):
        for repository in self.repositories_with_direct_users:
            repository.move_direct_users_to_teams()
