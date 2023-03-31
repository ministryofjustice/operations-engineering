import os


class Constants:
    """This class defines project-level constants"""

    # Added to fix error in command: python3 -m unittest discover python/test -v
    def __new__(cls, *_, **__):
        return super(Constants, cls).__new__(cls)

    def __init__(self):
        self.username = 0
        self.repository_name = 0
        self.permission = 1
        self.issue_section_enabled = 1
        self.operations_engineering_team_name = "operations-engineering"

        __org_name = os.getenv("ORG_NAME")
        if not __org_name:
            raise ValueError("The env variable ORG_NAME is empty or missing")
        self.org_name = __org_name

        __oauth_token = os.getenv("ADMIN_GITHUB_TOKEN")
        if not __oauth_token:
            raise ValueError(
                "The env variable ADMIN_GITHUB_TOKEN is empty or missing")
        self.oauth_token = __oauth_token
