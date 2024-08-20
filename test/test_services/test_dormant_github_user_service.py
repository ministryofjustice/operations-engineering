import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

from services.dormant_github_user_service import DormantGitHubUser
from services.github_service import GithubService


class TestDormantGitHubUser(unittest.TestCase):
    def setUp(self):
        self.github_service = MagicMock(spec=GithubService)
        self.username = "testuser"
        self.user = DormantGitHubUser(self.github_service, self.username)

    def test_email_is_cached(self):
        self.github_service.get_user_org_email_address.return_value = "test@example.com"
        email = self.user.email
        self.assertEqual(email, "test@example.com")
        # Ensure it is called only once
        self.github_service.get_user_org_email_address.assert_called_once_with(
            self.username
        )

    def test_last_github_activity_is_cached(self):
        last_activity_date = datetime.now() - timedelta(days=100)
        self.github_service.get_last_audit_log_activity_date_for_user.return_value = (
            last_activity_date
        )
        activity = self.user.last_github_activity
        self.assertEqual(activity, last_activity_date)
        self.github_service.get_last_audit_log_activity_date_for_user.assert_called_once_with(
            self.username
        )

    def test_is_dormant_when_no_activities(self):
        self.github_service.get_last_audit_log_activity_date_for_user.return_value = (
            None
        )
        self.user.fetch_last_auth0_activity = MagicMock(return_value=None)
        self.assertTrue(self.user.is_dormant)

    def test_is_not_dormant_when_recent_github_activity(self):
        self.github_service.get_last_audit_log_activity_date_for_user.return_value = (
            datetime.now()
        )
        self.user.fetch_last_auth0_activity = MagicMock(return_value=None)
        self.assertFalse(self.user.is_dormant)

    def test_is_not_dormant_when_recent_auth0_activity(self):
        self.github_service.get_last_audit_log_activity_date_for_user.return_value = (
            None
        )
        recent_activity = datetime.now() - timedelta(days=10)
        self.user.fetch_last_auth0_activity = MagicMock(return_value=recent_activity)
        self.assertFalse(self.user.is_dormant)

    def test_is_dormant_when_all_activities_are_old(self):
        old_activity = datetime.now() - timedelta(days=100)
        self.github_service.get_last_audit_log_activity_date_for_user.return_value = (
            old_activity
        )
        self.user.fetch_last_auth0_activity = MagicMock(return_value=old_activity)
        self.assertTrue(self.user.is_dormant)


class TestDormantGitHubUserCloudWatchIntegration(unittest.TestCase):
    def setUp(self):
        self.github_service = MagicMock(spec=GithubService)
        self.username = "testuser"
        self.user = DormantGitHubUser(
            self.github_service, self.username, days_considered_dormant=90
        )
        self.start_time = int((datetime.now() - timedelta(days=90)).timestamp())
        self.end_time = int(datetime.now().timestamp())
        self.query = "fields @timestamp, @message | sort @timestamp desc | limit 1"

    @patch("boto3.client")
    def test_execute_cloudwatch_query(self, mock_boto_client):
        mock_client = MagicMock()
        mock_boto_client.return_value = mock_client
        mock_client.start_query.return_value = {"queryId": "12345"}

        query_id = self.user.execute_cloudwatch_query(
            self.query, self.start_time, self.end_time
        )

        mock_boto_client.assert_called_once_with("logs", region_name="eu-west-2")
        mock_client.start_query.assert_called_once_with(
            logGroupName="/aws/events/LogsFromOperationsEngineeringAuth0",
            startTime=self.start_time,
            endTime=self.end_time,
            queryString=self.query,
        )
        self.assertEqual(query_id, "12345")

    @patch("boto3.client")
    def test_get_cloudwatch_query_results(self, mock_boto_client):
        mock_client = MagicMock()
        mock_boto_client.return_value = mock_client
        mock_client.get_query_results.side_effect = [
            {"status": "Running", "results": []},
            {"status": "Complete", "results": [{"value": "2021-01-01 00:00:00.000"}]},
        ]

        results = self.user.get_cloudwatch_query_results("12345")

        mock_boto_client.assert_called_once_with("logs", region_name="eu-west-2")
        self.assertEqual(mock_client.get_query_results.call_count, 2)
        self.assertEqual(results, [{"value": "2021-01-01 00:00:00.000"}])


if __name__ == "__main__":
    unittest.main()
