from python.lib.helpers import Helpers


class Team:
    """A struct to store team info ie name, users, repos, GH ID"""

    def __init__(self, helpers: Helpers, name: str):
        self.helpers = helpers
        self.name = name
        self.users_usernames = self.helpers.fetch_team_users_usernames(
            self.name)
        self.repositories_and_permissions = self.helpers.fetch_team_repositories_and_permissions(
            self.name)
        self.id = self.helpers.get_team_id_from_team_name(self.name)

    def add_new_team_user(self, user_username: str):
        self.users_usernames.append(user_username)
