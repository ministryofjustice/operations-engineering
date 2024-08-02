import boto3
import time
from botocore.exceptions import ClientError
from datetime import datetime, timedelta

class CloudtrailService:
    def __init__(self) -> None:
        self.client = boto3.client("cloudtrail", region_name="eu-west-2")

    def get_active_users_for_dormant_users_process(self):
        username_key = "eventData.useridentity.principalid"
        data_store_id = "ec682140-3e75-40c0-8e04-f06207791c2e"
        period_cutoff = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d %H:%M:%S')

        query_string = f"""
        SELECT DISTINCT {username_key}
        FROM {data_store_id}
        WHERE eventTime > '{period_cutoff}';
        """

        query_id = self.client.start_query(QueryStatement=query_string)['QueryId']

        return self.get_query_results(query_id)

    # pylint: disable=W0719
    def get_query_results(self, query_id):
        while True:
            status = self.client.get_query_results(QueryId=query_id)['QueryStatus']
            print(f"Query status: {status}")
            if status in ['FAILED', 'CANCELLED', 'TIMED_OUT']:
                raise ClientError(
                    {
                        'Error': {
                            'Code': status,
                            'Message': f"Cloudtrail data lake query failed with status: {status}"
                        }
                    },
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
