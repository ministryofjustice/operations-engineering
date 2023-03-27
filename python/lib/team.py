from python.lib import helpers


class Team:
    """A struct to store team info ie name, users, repos, GH ID"""

    def __init__(self, github_service, name):
        self.github_service = github_service
        self.name = name
        self.users_usernames = helpers.fetch_team_users_usernames(
            self.github_service, self.name
        )
        self.repositories_and_permissions = (
            helpers.fetch_team_repositories_and_permissions(
                self.github_service, self.name
            )
        )
        self.id = self.github_service.get_team_id_from_team_name(self.name)

    def correct_team_name(self):
        """GH team names use a slug name. This
        swaps ., _, , with a - and lower cases
        the team name
        Returns:
            string: converted team name
        """
        temp_name = ""
        new_team_name = ""

        temp_name = self.name
        temp_name = temp_name.replace(".", "-")
        temp_name = temp_name.replace("_", "-")
        temp_name = temp_name.replace(" ", "-")
        temp_name = temp_name.replace("---", "-")
        temp_name = temp_name.replace("--", "-")

        if temp_name.startswith(".") or temp_name.startswith("-"):
            temp_name = temp_name[1:]

        if temp_name.endswith(".") or temp_name.endswith("-"):
            temp_name = temp_name[:-1]

        new_team_name = temp_name.lower()

        return new_team_name
