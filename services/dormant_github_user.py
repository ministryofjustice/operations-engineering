from datetime import datetime

from services.auth0_service import Auth0Service
from services.github_service import GithubService


class DormantGitHubUser():
    def __init__(self, github_service: GithubService, auth0_service: Auth0Service, name: str):
        self.github_service = github_service
        self.auth0_service = auth0_service
        self.name = name
        self.email: str
        self.last_auth0_activity: datetime | None
        self.last_github_activity: datetime | None

        self.get_email_address_from_github()
        self.get_last_github_audit_log_activity()
        self.get_last_auth0_audit_log_activity()

    def get_email_address_from_github(self):
        self.email = self.github_service.get_user_org_email_address(self.name)

    def get_last_github_audit_log_activity(self):
        self.last_auth0_activity = self.github_service.get_last_audit_log_activity(
            self.name)

    def get_last_auth0_audit_log_activity(self):
        self.auth0_service.get_last_audit_log_activity(self.name)
