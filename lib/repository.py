from github import Team

from services.github_service import GithubService

# Refactor Status: Done
# Moved to move_users_to_teams_refactor.py


class RepositoryTeam:
    def __init__(self, team: Team):
        self.name = team.name.lower()
        self.users_usernames = [
            member.login.lower()
            for member in team.get_members()
        ]
        self.repository_permission = team.permission
        self.id = team.id

# Refactor Status: Done
# Class moved to move_users_to_teams_refactor.py


class Repository:
    # Added to stop TypeError on instantiation. See https://github.com/python/cpython/blob/d2340ef25721b6a72d45d4508c672c4be38c67d3/Objects/typeobject.c#L4444
    def __new__(cls, *_, **__):
        return super(Repository, cls).__new__(cls)

    # Refactor Status: Done
    # Moved to move_users_to_teams_refactor.py
    def __init__(self, github_service: GithubService, name: str,
                 issue_section_status: bool, users_with_direct_access: list[str], ops_eng_team_user_names: list[str],
                 ignore_teams: list):
        self.github_service = github_service
        self.name = name.lower()
        self.issue_section_enabled = issue_section_status
        self.ops_eng_team_user_names = ops_eng_team_user_names
        self.direct_users = users_with_direct_access
        self.ignore_teams = ignore_teams
        self.teams = []
        self.get_existing_teams()

    # Refactor Status: Done
    # Moved to is_new_team_needed() in move_users_to_teams_refactor.py
    def is_new_team_needed(self, permission: str) -> bool:
        new_team_required = True
        expected_team_name = self.form_team_name(permission.lower())
        for team in self.teams:
            if team.name.lower() == expected_team_name.lower():
                new_team_required = False
                break
        return new_team_required

    # Refactor Status: Done
    # Moved to ensure_repository_teams_exists() in move_users_to_teams_refactor.py
    def ensure_repository_teams_exists(self):
        """ Check if a automated team with the required permission already
            exists and if not creates a new team for the repository
        """
        for direct_user_username in self.direct_users:
            permission = self.github_service.get_user_permission_for_repository(
                direct_user_username, self.name)
            if self.is_new_team_needed(permission):
                team_name = self.form_team_name(permission)
                # Create a team on GitHub
                team_id = self.create_a_team_on_github(team_name)
                if team_id > 0:
                    self.github_service.amend_team_permissions_for_repository(
                        team_id, permission, self.name)
                    self.remove_operations_engineering_team_users_from_team(
                        team_id)
                    # Create and store a Team object locally
                    for team in self.github_service.get_repository_teams(self.name):
                        if team.name == team_name:
                            self.add_team(team)

    # Refactor Status: Done
    # Not needed
    def add_team(self, team):
        self.teams.append(RepositoryTeam(team))

    # Refactor Status: Done
    # Moved to put_users_into_repository_teams() in move_users_to_teams_refactor.py
    def put_direct_users_into_teams(self):
        for direct_user_username in self.direct_users:
            for team in self.teams:
                permission = self.github_service.get_user_permission_for_repository(
                    direct_user_username, self.name)
                expected_team_name = self.form_team_name(permission)
                if team.name == expected_team_name:
                    if len(team.users_usernames) == 0 or permission == "admin":
                        self.github_service.add_user_to_team_as_maintainer(
                            direct_user_username, team.id)
                    else:
                        self.github_service.add_user_to_team(
                            direct_user_username, team.id)
                    break

    # Refactor Status: Done
    # Moved to raise_issue_on_repository() in move_users_to_teams_refactor.py
    def create_repo_issues_for_direct_users(self):
        for direct_user_username in self.direct_users:
            if self.issue_section_enabled:
                self.github_service.create_an_access_removed_issue_for_user_in_repository(
                    direct_user_username, self.name)

    # Refactor Status: Done
    # Not used
    def remove_direct_users_access(self):
        for direct_user_username in self.direct_users:
            self.github_service.remove_user_from_repository(
                direct_user_username, self.name)

    # Refactor Status: Done
    # Moved to remove_operations_engineering_team_users_from_team() in move_users_to_teams_refactor.py
    def remove_operations_engineering_team_users_from_team(self, team_id: int):
        """When team is created GH adds the user who ran the GH action to the team
           this function removes the user from that team
        """
        for user_username in self.ops_eng_team_user_names:
            self.github_service.remove_user_from_team(user_username, team_id)

    # Refactor Status: Done
    # Moved to create_a_team_on_github() in move_users_to_teams_refactor.py
    def create_a_team_on_github(self, team_name: str) -> int:
        team_id = 0
        if not self.github_service.team_exists(team_name):
            self.github_service.create_new_team_with_repository(
                team_name, self.name)
            team_id = self.github_service.get_team_id_from_team_name(team_name)
        return team_id

    # Refactor Status: Done
    # Moved to form_team_name() in move_users_to_teams_refactor.py
    def form_team_name(self, users_permission: str) -> str:
        """ GH team names use a slug name. This swaps ., _, , with
            a - and then lower cases the team name
        """
        temp_name = self.name + "-" + users_permission + "-team"
        temp_name = temp_name.replace(".", "-")
        temp_name = temp_name.replace("_", "-")
        temp_name = temp_name.replace(" ", "-")
        temp_name = temp_name.replace("---", "-")
        temp_name = temp_name.replace("--", "-")
        temp_name = temp_name.replace("--", "-")

        if temp_name.startswith(".") or temp_name.startswith("-"):
            temp_name = temp_name[1:]

        return temp_name.lower()

    # Refactor Status: Done
    # Moved to get_repository_teams() in move_users_to_teams_refactor.py
    def get_existing_teams(self):
        self.teams = [
            RepositoryTeam(team)
            for team in self.github_service.get_repository_teams(self.name)
            # ignore teams in the ignore list
            if team.name.lower() not in self.ignore_teams
        ]

    # Refactor Status: Done
    # Moved to remove_repository_users_with_team_access() in move_users_to_teams_refactor.py
    def remove_users_already_in_existing_teams(self):
        removed_users = []
        for team in self.teams:
            for direct_user_username in self.direct_users:
                if direct_user_username in team.users_usernames:
                    permission = self.github_service.get_user_permission_for_repository(
                        direct_user_username, self.name)
                    if permission == team.repository_permission:
                        if self.issue_section_enabled:
                            self.github_service.create_an_access_removed_issue_for_user_in_repository(
                                direct_user_username, self.name)
                        self.github_service.remove_user_from_repository(
                            direct_user_username, self.name)
                        removed_users.append(direct_user_username)

        self.direct_users[:] = [
            direct_user
            for direct_user in self.direct_users
            if direct_user not in removed_users
        ]

    # Refactor Status: Done
    # Not needed
    def move_remaining_users_to_new_teams(self):
        self.ensure_repository_teams_exists()
        self.put_direct_users_into_teams()
        self.create_repo_issues_for_direct_users()
        self.remove_direct_users_access()

    # Refactor Status: Done
    # Not needed
    def move_direct_users_to_teams(self):
        self.remove_users_already_in_existing_teams()
        self.move_remaining_users_to_new_teams()
