import os

from pyaml_env import parse_config

from python.lib.repository import Repository
from python.services.github_service import GithubService


class Organisation:
    # Added to stop TypeError on instantiation. See https://github.com/python/cpython/blob/d2340ef25721b6a72d45d4508c672c4be38c67d3/Objects/typeobject.c#L4444
    def __new__(cls, *_, **__):
        return super(Organisation, cls).__new__(cls)

    # Refactor Status: Done
    # Moved to get_repositories_with_direct_users() and main() in move_users_to_teams_refactor.py
    def __init__(self, github_service: GithubService, org_name: str):
        self.repository_name = 0

        self.ignore_teams = []
        self.badly_named_repositories = []
        self.__load_config()

        self.org_name = org_name.lower()
        self.github_service = github_service

        self.ops_eng_team_user_usernames = self.github_service.get_a_team_usernames(
            "operations-engineering")

        self.outside_collaborators = self.github_service.get_outside_collaborators_login_names()

        # A list of tuples containing pre info for the repository objects
        self.repositories = []
        self.__fetch_repositories()

        # A list of repository objects
        self.repositories_with_direct_users = []
        self.__create_repositories_with_direct_users()

    # Refactor Status: Not needed
    # Using lists in move_users_to_teams_refactor.py instead of config file
    # See get_ignore_teams_list() and get_ignore_repositories_list()
    # TODO: Remove the config file/a and related config file test/s
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

    # Refactor Status: Done
    # Moved to get_org_repositories() in move_users_to_teams_refactor.py
    def __fetch_repositories(self):
        self.repositories = [
            repository
            for repository in self.__fetch_repository_info()
            # ignore repositories in the badly_named_repositories list
            if repository[self.repository_name].lower() not in self.badly_named_repositories
        ]

    # Refactor Status: Done
    # Moved to get_repositories_with_direct_users() in move_users_to_teams_refactor.py
    def __create_repositories_with_direct_users(self):
        issue_section_enabled = 1
        for repository in self.repositories:
            users_with_direct_access = self.__fetch_users_with_direct_access(
                repository)
            if len(users_with_direct_access) > 0:
                self.repositories_with_direct_users.append(
                    Repository(
                        self.github_service,
                        repository[self.repository_name].lower(),
                        repository[issue_section_enabled],
                        users_with_direct_access,
                        self.ops_eng_team_user_usernames,
                        self.ignore_teams
                    )
                )

    # Refactor Status: Done
    # Moved to get_repo_direct_access_users() in move_users_to_teams_refactor.py
    def __fetch_users_with_direct_access(self, repository: tuple):
        users_with_direct_access = []
        number_of_direct_users = 2
        if repository[number_of_direct_users] > 0:
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
