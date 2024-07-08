import boto3
import time
from datetime import datetime, timedelta

class CloudtrailService:
    def __init__(self) -> None:
        self.client = boto3.client("cloudtrail")


    def get_active_users(self):

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


    def get_query_results(self, query_id):
        while True:
            response = self.client.get_query_results(QueryId=query_id)
            status = response['QueryStatus']
            print(f"Query status: {status}")
            if status in ['FAILED', 'CANCELLED', 'TIMED_OUT']:
                raise Exception(f"Cloudtrail data lake query failsed with status: {status}")
            elif status == 'FINISHED':
                return [list(row[0].values())[0] for row in response['QueryResultRows']]
            time.sleep(20)

    def get_query_status(self, query_id):
        response = self.client.get_query_status(QueryId=query_id)

        return response['QueryStatus']
