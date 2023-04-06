import logging
from python.services.github_service import GithubService


class Helpers:
    """_summary_"""

    def __init__(self, github_service: GithubService):
        self.github_service = github_service

    def fetch_repo_names_and_issue_section_enabled(self) -> list[tuple]:
        has_next_page = True
        after_cursor = None
        repositories = []

        while has_next_page:
            data = self.github_service.get_paginated_list_of_repositories(
                after_cursor)

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
                                repository["node"]["name"].lower(),
                                repository["node"]["hasIssuesEnabled"],
                            )
                        )

            has_next_page = data["organization"]["repositories"]["pageInfo"]["hasNextPage"]
            after_cursor = data["organization"]["repositories"]["pageInfo"]["endCursor"]

        return repositories

    def fetch_repository_users_with_direct_access_to_repository(self, repository_name: str) -> list[str]:
        has_next_page = True
        after_cursor = None
        users_usernames = []

        while has_next_page:
            data = self.github_service.get_paginated_list_of_user_names_with_direct_access_to_repository(
                repository_name, after_cursor
            )

            if data["repository"]["collaborators"]["edges"] is not None:
                for repository in data["repository"]["collaborators"]["edges"]:
                    users_usernames.append(repository["node"]["login"].lower())

            has_next_page = data["repository"]["collaborators"]["pageInfo"]["hasNextPage"]
            after_cursor = data["repository"]["collaborators"]["pageInfo"]["endCursor"]

        return users_usernames

    def fetch_team_names(self) -> list[str]:
        has_next_page = True
        after_cursor = None
        team_names = []

        while has_next_page:
            data = self.github_service.get_paginated_list_of_team_names(
                after_cursor)

            if data["organization"]["teams"]["edges"] is not None:
                for team in data["organization"]["teams"]["edges"]:
                    team_names.append(team["node"]["slug"].lower())

            has_next_page = data["organization"]["teams"]["pageInfo"]["hasNextPage"]
            after_cursor = data["organization"]["teams"]["pageInfo"]["endCursor"]

        return team_names

    def fetch_team_users_usernames(self, team_name: str) -> list[str]:
        has_next_page = True
        after_cursor = None
        user_usernames = []

        while has_next_page:
            data = self.github_service.get_paginated_list_of_team_user_names(
                team_name, after_cursor
            )

            if data["organization"]["team"]["members"]["edges"] is not None:
                for team in data["organization"]["team"]["members"]["edges"]:
                    user_usernames.append(team["node"]["login"].lower())

            has_next_page = data["organization"]["team"]["members"]["pageInfo"][
                "hasNextPage"
            ]
            after_cursor = data["organization"]["team"]["members"]["pageInfo"]["endCursor"]

        return user_usernames

    def fetch_team_repositories_and_permissions(self, team_name: str) -> list[tuple]:
        has_next_page = True
        after_cursor = None
        repositories = []

        while has_next_page:
            data = self.github_service.get_paginated_list_of_team_repositories_and_permissions(
                team_name, after_cursor
            )

            if data["organization"]["team"]["repositories"]["edges"] is not None:
                for repository in data["organization"]["team"]["repositories"]["edges"]:
                    repositories.append(
                        (repository["node"]["name"].lower(),
                         repository["permission"])
                    )

            has_next_page = data["organization"]["team"]["repositories"]["pageInfo"][
                "hasNextPage"
            ]
            after_cursor = data["organization"]["team"]["repositories"]["pageInfo"][
                "endCursor"
            ]

        return repositories

    def get_team_id_from_team_name(self, name) -> int:
        return self.github_service.get_team_id_from_team_name(name)
