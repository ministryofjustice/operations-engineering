import time
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

    @property
    def is_dormant(self) -> bool:
        if self.last_github_activity is None and self.last_auth0_activity is None:
            return True

        if self.last_github_activity is None:
            return self.last_auth0_activity < self.threshold

        if self.last_auth0_activity is None:
            return self.last_github_activity < self.threshold

        return self.last_github_activity < self.threshold and self.last_auth0_activity < self.threshold

    def execute_cloudwatch_query(self, query, start_time, end_time):
        client = boto3.client('logs', region_name='eu-west-2')
        query_response = client.start_query(
            logGroupName='/aws/events/LogsFromOperationsEngineeringAuth0',
            startTime=start_time,
            endTime=end_time,
            queryString=query,
        )
        return query_response['queryId']

    def get_cloudwatch_query_results(self, query_id):
        """Polls CloudWatch Logs for query results and returns the results when complete."""
        client = boto3.client('logs', region_name='eu-west-2')
        while True:
            response = client.get_query_results(queryId=query_id)
            if response['status'] == 'Complete':
                return response['results']
            time.sleep(1)  # Sleep to rate limit the polling

    def format_timestamp(self, timestamp):
        return datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f").strftime("%Y-%m-%d %H:%M:%S")

    def fetch_last_auth0_activity(self):
        """Fetches the last activity timestamp for the user from Auth0 logs.
        The Auth0 logs are stored in CloudWatch Logs and are queried using the user's email address."""
        query = f"""
        fields @timestamp, @message
        | parse @message '"user_name":"*"' as user_name
        | filter user_name = '{self._email}'
        | sort @timestamp desc
        | limit 1
        """
        start_time = int(self.threshold.timestamp())
        end_time = int(datetime.now().timestamp())

        query_id = self.execute_cloudwatch_query(query, start_time, end_time)
        results = self.get_cloudwatch_query_results(query_id)
        if results:
            timestamp = results[0][0]['value']
            return self.format_timestamp(timestamp)
        return None
