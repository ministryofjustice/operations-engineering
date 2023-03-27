from .constants import Constants
from python.lib import helpers


class Repository:
    """The repository class"""

    def __init__(self, github_service, name, issue_section_status, collaborators):
        self.constants = Constants()
        self.github_service = github_service
        self.name = name
        self.issue_section_enabled = issue_section_status
        self.direct_users = helpers.fetch_repository_users_usernames_and_permissions(
            self.github_service, self.name
        )
        self.org_collaborators = collaborators
        self.teams = []

        # Remove a repository collaborator/s from the direct_users list
        self.direct_users[:] = [
            user_username
            for user_username in self.direct_users
            if user_username[self.constants.name] not in self.org_collaborators
        ]

    def add_team(self, new_team):
        """A a Team object to the repository object
        Args:
            new_team (Team): a Team object
        """
        self.teams.append(new_team)

    def remove_direct_users(self):
        """_summary_
        Returns:
            _type_: _description_
        """
        #     remaining_users = users_not_in_a_team

        #     for username in users_not_in_a_team:
        #         put_user_into_existing_team(self.github_service, repository.name, username, remaining_users, org_teams)

        #     put_users_into_new_team(github_service, repository.name, remaining_users)
