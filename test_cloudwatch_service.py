import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

from services.cloudwatch_service import CloudWatchService


class TestCloudWatchService(unittest.TestCase):

    @patch('services.cloudwatch_service.boto3.Session')
    def test_init(self, mock_boto_session):
        mock_client = MagicMock()
        mock_boto_session.return_value.client.return_value = mock_client

        service = CloudWatchService(log_group_name='test-log-group')

        mock_boto_session.return_value.client.assert_called_with(
            "logs", region_name="eu-west-2")
        self.assertEqual(service.log_group_name, 'test-log-group')
        self.assertEqual(service.client, mock_client)

    @patch('services.cloudwatch_service.boto3.Session')
    def test_run_insights_query(self, mock_boto_session):
        mock_client = MagicMock()
        mock_boto_session.return_value.client.return_value = mock_client

        mock_client.start_query.return_value = {"queryId": "test-query-id"}

        service = CloudWatchService(log_group_name='test-log-group')
        query_id = service.run_insights_query(
            "test-query", 1609459200, 1612137600)

        mock_client.start_query.assert_called_with(
            logGroupName='test-log-group',
            startTime=1609459200,
            endTime=1612137600,
            queryString="test-query",
        )
        self.assertEqual(query_id, "test-query-id")

    @patch('services.cloudwatch_service.boto3.Session')
    def test_poll_insights_query_for_results(self, mock_boto_session):
        mock_client = MagicMock()
        mock_boto_session.return_value.client.return_value = mock_client

        mock_client.get_query_results.side_effect = [
            {"status": "Running"},
            {"status": "Complete", "results": [["result1"], ["result2"]]},
        ]

        service = CloudWatchService(log_group_name='test-log-group')
        results = service.poll_insights_query_for_results("test-query-id")

        mock_client.get_query_results.assert_called_with(
            queryId="test-query-id")
        self.assertEqual(results, [["result1"], ["result2"]])

    @patch('services.cloudwatch_service.boto3.Session')
    @patch('services.cloudwatch_service.CloudWatchService.poll_insights_query_for_results')
    @patch('services.cloudwatch_service.CloudWatchService.run_insights_query')
    def test_get_all_auth0_users_that_appear_in_tenants(self, mock_run_query, mock_poll_results, mock_boto_session):
        mock_client = MagicMock()
        mock_boto_session.return_value.client.return_value = mock_client

        mock_run_query.return_value = "test-query-id"
        mock_poll_results.return_value = [
            [{"field": "user_name", "value": "user1@example.com"}],
            [{"field": "user_name", "value": "user2@example.com"}],
            [{"field": "user_name", "value": "invalid-user"}],
        ]

        service = CloudWatchService(log_group_name='test-log-group')
        result = service.get_all_auth0_users_that_appear_in_tenants()

        expected_query = """
        fields @timestamp, @message
        | parse @message '"user_name":"*"' as user_name
        | stats count() by user_name
        """
        start_time = int((datetime.now() - timedelta(days=90)).timestamp())
        end_time = int(datetime.now().timestamp())

        mock_run_query.assert_called_with(expected_query, start_time, end_time)

        self.assertEqual(result, ['user1@example.com', 'user2@example.com'])


if __name__ == "__main__":
    unittest.main()
