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

    def get_query_results(self, query_id):
        while True:
            status = self.client.get_query_results(QueryId=query_id)['QueryStatus']
            print(f"Query status: {{status}}")
            if status in ['FAILED', 'CANCELLED', 'TIMED_OUT']:
                raise ClientError(
                    {{
                        'Error': {{
                            'Code': status,
                            'Message': f"Cloudtrail data lake query failed with status: {{status}}"
                        }}
                    }},
                    operation_name='get_query_results'
                )
            if status == 'FINISHED':
                return self.extract_query_results(query_id)
            time.sleep(20)

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

    @patch.object(CloudtrailService, "extract_query_results")
    @mock_aws
    def test_get_query_results_if_success(self, mock_extract_query_results):
        mock_active_users = ["user1", "user2", "user3"]
        mock_extract_query_results.return_value = mock_active_users
        self.cloudtrail_service.client.get_query_results = MagicMock(return_value={{'QueryStatus': 'FINISHED'}})
        mock_query_id = "mock_id"

        response = self.cloudtrail_service.get_query_results(mock_query_id)

        self.cloudtrail_service.client.get_query_results.assert_called_once_with(QueryId=mock_query_id)
        mock_extract_query_results.assert_called_once_with(mock_query_id)
        assert response == mock_active_users

    @mock_aws
    def test_get_query_results_if_fail(self):
        self.cloudtrail_service.client.get_query_results = MagicMock(return_value={{'QueryStatus': 'CANCELLED'}})
        with self.assertRaises(ClientError) as context:
            self.cloudtrail_service.get_query_results("mock_id")

        self.cloudtrail_service.client.get_query_results.assert_called_once_with(QueryId="mock_id")
        self.assertEqual(str(context.exception), "An error occurred (CANCELLED) when calling the get_query_results operation: Cloudtrail data lake query failed with status: CANCELLED")

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

Please abide exactly by these rules when crafting your response:

- Do not acknowledge the question asked.
- Do not include any extra information.
- Do not explain your answers.
- Only produce the test code, nothing else.
"""
