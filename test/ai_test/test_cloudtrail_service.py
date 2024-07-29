import unittest
import boto3
from unittest.mock import patch, MagicMock, call
from botocore.exceptions import ClientError
from moto import mock_aws
from services.cloudtrail_service import CloudtrailService
from freezegun import freeze_time
from datetime import datetime, timedelta

class TestCloudtrailService(unittest.TestCase):

    @mock_aws
    def setUp(self):
        self.cloudtrail_service = CloudtrailService()
        self.cloudtrail_service.client = boto3.client("cloudtrail", region_name="us-west-2")

    @freeze_time("2024-07-11 00:00:00")
    @patch.object(CloudtrailService, "get_query_results")
    @mock_aws
    def test_get_active_users_for_dormant_users_process(self, mock_query_results):
        mock_active_users = ["user1", "user2", "user3"]
        mock_query_results.return_value = mock_active_users
        self.cloudtrail_service.client.start_query = MagicMock(return_value={"QueryId": "mock_query_id_with_valid_length"})
        mock_query_string = """
        SELECT DISTINCT eventData.useridentity.username
        FROM asdikajsndasondasodn
        WHERE eventTime > '2024-04-12 00:00:00';
        """

        assert self.cloudtrail_service.get_active_users_for_dormant_users_process() == mock_active_users
        self.cloudtrail_service.client.start_query.assert_called_once_with(QueryStatement=mock_query_string)

    @patch.object(CloudtrailService, "extract_query_results")
    @mock_aws
    def test_get_query_results_if_success(self, mock_extract_query_results):
        mock_active_users = ["user1", "user2", "user3"]
        mock_extract_query_results.return_value = mock_active_users
        self.cloudtrail_service.client.get_query_results = MagicMock(return_value={'QueryStatus': 'FINISHED'})
        mock_query_id = "mock_query_id_with_valid_length"

        response = self.cloudtrail_service.get_query_results(mock_query_id)

        self.cloudtrail_service.client.get_query_results.assert_called_once_with(QueryId=mock_query_id)
        mock_extract_query_results.assert_called_once_with(mock_query_id)
        assert response == mock_active_users

    @mock_aws
    def test_get_query_results_if_fail(self):
        self.cloudtrail_service.client.get_query_results = MagicMock(return_value={'QueryStatus': 'CANCELLED'})
        with self.assertRaises(ClientError) as context:
            self.cloudtrail_service.get_query_results("mock_query_id_with_valid_length")

        self.cloudtrail_service.client.get_query_results.assert_called_once_with(QueryId="mock_query_id_with_valid_length")
        self.assertEqual(str(context.exception), "An error occurred (CANCELLED) when calling the get_query_results operation: Cloudtrail data lake query failed with status: CANCELLED")

    # pylint: disable=C0103, W0613
    @mock_aws
    def test_extract_query_results(self):
        mock_next_token = "mock_next_token"

        def mock_get_query_results(QueryId=None, MaxQueryResults=1000, NextToken=False):
            if NextToken:
                return {'QueryResultRows': [[{'username': 'test_user3'}]]}

            return {'NextToken': mock_next_token, 'QueryResultRows': [[{'username': 'test_user1'}], [{'username': 'test_user2'}]]}

        self.cloudtrail_service.client.get_query_results = MagicMock(side_effect=mock_get_query_results)
        mock_query_id = "mock_query_id_with_valid_length"

        assert self.cloudtrail_service.extract_query_results(mock_query_id) == ["test_user1", "test_user2", "test_user3"]
        self.cloudtrail_service.client.get_query_results.assert_has_calls([call(QueryId=mock_query_id, MaxQueryResults=1000), call(QueryId=mock_query_id, MaxQueryResults=1000, NextToken=mock_next_token)])

    @freeze_time("2023-05-01 00:00:00")
    @mock_aws
    def test_get_active_users_for_dormant_users_process_period_cutoff(self):
        mock_query_id = "asdasojdnaspodinaspodiahsasdasdopiasuhdpoaishdjaspoihj"
        self.cloudtrail_service.client.start_query = MagicMock(return_value={"QueryId": mock_query_id})
        mock_query_string = """
        SELECT DISTINCT eventData.useridentity.username
        FROM asdikajsndasondasodn
        WHERE eventTime > '2023-01-31 00:00:00';
        """

        self.cloudtrail_service.get_active_users_for_dormant_users_process()
        self.cloudtrail_service.client.start_query.assert_called_once_with(QueryStatement=mock_query_string)
