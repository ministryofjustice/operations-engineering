from github import Team

class Team:
    """A struct to store team info ie name, users, repos, GH ID"""

    def __init__(self, team: Team):
        self.name = team.name.lower()
        self.users_usernames = [
            member.login.lower()
            for member in team.get_members()
        ]
        self.repository_permission = team.permission
        self.id = team.id

    def add_new_team_user(self, user_username: str):
        self.users_usernames.append(user_username)
