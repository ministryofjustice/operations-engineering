PROMPT_TEMPLATE = """
Given this context:
{context}
Please generate unit tests, using the Python unittest library, for the following functions:

{modified_functions}

For example, given this context:

import boto3
import time
from botocore.exceptions import ClientError
from datetime import datetime, timedelta

class CloudtrailService:
    def __init__(self) -> None:
        self.client = boto3.client("cloudtrail", region_name="eu-west-2")

And given these functions:

    def extract_query_results(self, query_id):
        response = self.client.get_query_results(QueryId=query_id, MaxQueryResults=1000)
        active_users = [list(row[0].values())[0] for row in response['QueryResultRows']]

        if "NextToken" in response:
            next_token = response["NextToken"]

            while True:
                response = self.client.get_query_results(QueryId=query_id, MaxQueryResults=1000, NextToken=next_token)
                active_users = active_users + [list(row[0].values())[0] for row in response['QueryResultRows']]
                if "NextToken" in response:
                    next_token = response["NextToken"]
                else:
                    break

        return active_users

These are the expected unit tests:

    @mock_aws
    def test_extract_query_results(self):
        mock_next_token = "mock_next_token"

        def mock_get_query_results(QueryId=None, MaxQueryResults=1000, NextToken=False):
            if NextToken:
                return {{'QueryResultRows': [[{{'principalId': 'test_user3'}}]]}}

            return {{'NextToken': mock_next_token, 'QueryResultRows': [[{{'principalId': 'test_user1'}}], [{{'principalId': 'test_user2'}}]]}}

        self.cloudtrail_service.client.get_query_results = MagicMock(side_effect=mock_get_query_results)
        mock_query_id = "mock_id"

        assert self.cloudtrail_service.extract_query_results(mock_query_id) == ["test_user1", "test_user2", "test_user3"]
        self.cloudtrail_service.client.get_query_results.assert_has_calls([call(QueryId=mock_query_id, MaxQueryResults=1000), call(QueryId=mock_query_id, MaxQueryResults=1000, NextToken=mock_next_token)])
"""
