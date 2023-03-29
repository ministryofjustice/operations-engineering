import os


class Constants:
    """This class defines project-level constants"""

    # Added to fix error in command: python3 -m unittest discover python/test -v
    def __new__(cls, *_, **__):
        return super(Constants, cls).__new__(cls)

    def __init__(self):
        self.name = 0
        self.permission = 1
        self.issue_section_enabled = 1

    def get_org_name(self):
        org_name = os.getenv("ORG_NAME")
        if org_name == "" or org_name is None:
            raise ValueError("The env variable ORG_NAME is empty or missing")
        return org_name

    def get_oauth_token(self):
        oauth_token = os.getenv("ADMIN_GITHUB_TOKEN")
        if oauth_token == "" or oauth_token is None:
            raise ValueError(
                "The env variable ADMIN_GITHUB_TOKEN is empty or missing")
        return oauth_token
