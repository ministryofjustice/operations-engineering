from datetime import datetime, timedelta

import boto3

from services.github_service import GithubService


class DormantGitHubUser:
    def __init__(self, github_service: GithubService, name: str, days_considered_dormant: int = 90):
        self.github_service = github_service
        self.name = name
        self.threshold = datetime.now() - timedelta(days=days_considered_dormant)
        self._email = None
        self._last_github_activity = None
        self._last_auth0_activity = None

    @property
    def email(self):
        if self._email is None:
            self._email = self.github_service.get_user_org_email_address(
                self.name)
        return self._email

    @property
    def last_github_activity(self):
        if self._last_github_activity is None:
            self._last_github_activity = self.github_service.get_last_audit_log_activity_date_for_user(
                self.name)
        return self._last_github_activity

    @property
    def last_auth0_activity(self):
        if self._last_auth0_activity is None:
            self._last_auth0_activity = self.fetch_last_auth0_activity()
        return self._last_auth0_activity

    def fetch_last_auth0_activity(self):
        client = boto3.client('logs', region_name='eu-west-2')
        response = client.filter_log_events(
            logGroupName="/aws/events/LogsFromOperationsEngineeringAuth0",
        )
        events = response['events']
        # Process events to find the latest activity
        # Assume the last event is the latest activity for simplicity
        if events:
            return events[-1]['timestamp']
        return None
