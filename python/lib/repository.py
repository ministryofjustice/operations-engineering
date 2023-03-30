from python.services.github_service import GithubService
from python.lib.constants import Constants
from python.lib.team import Team
from python.lib.helpers import Helpers


class Repository:
    """The repository class"""

    def __init__(self, github_service: GithubService, name: str, issue_section_status: bool, collaborators: list):
        self.constants = Constants()
        self.helper = Helpers(github_service)
        self.github_service = github_service
        self.name = name
        self.issue_section_enabled = issue_section_status
        self.org_collaborators = collaborators
        self.teams = []

        self.__direct_users = self.helper.fetch_repository_users_usernames(
            self.name)

        # Remove a repository collaborator/s from the direct_users list
        self.__direct_users[:] = [
            user_username
            for user_username in self.__direct_users
            if user_username not in self.org_collaborators
        ]

        self.direct_users_and_permission = []
        for user_username in self.__direct_users:
            user_permission = github_service.get_user_permission_for_repository(
                user_username, self.name)
            self.direct_users_and_permission.append(
                (user_username, user_permission))

    def add_team(self, new_team: Team):
        self.teams.append(new_team)

    def is_new_team_needed(self, permission: str) -> bool:
        new_team_required = True
        expected_team_name = self.helper.form_team_name(self.name, permission)
        for team in self.teams:
            if team.name == expected_team_name:
                new_team_required = False
                break
        return new_team_required
