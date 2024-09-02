import logging
import re
import time
from datetime import datetime, timedelta

import boto3

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class CloudWatchService:
    def __init__(self, log_group_name) -> None:
        session = boto3.Session()
        self.client = session.client("logs", region_name="eu-west-2")
        self.log_group_name = log_group_name

    def run_insights_query(self, query, start_time, end_time):
        query_response = self.client.start_query(
            logGroupName=self.log_group_name,
            startTime=start_time,
            endTime=end_time,
            queryString=query,
        )
        return query_response["queryId"]

    def poll_insights_query_for_results(self, query_id, timeout=300):
        """Polls CloudWatch Logs for query results and returns the results when complete."""
        start_time = time.time()
        while True:
            response = self.client.get_query_results(queryId=query_id)
            if response["status"] == "Complete":
                return response["results"]
            if time.time() - start_time > timeout:
                logger.error("Query timed out")
                return None
            time.sleep(1)  # Sleep to rate limit the polling

    def get_all_auth0_users_that_appear_in_tenants(self, days_to_check=90):
        query = """
        fields @timestamp, @message
        | parse @message '"user_name":"*"' as user_name
        | stats count() by user_name
        """
        start_time = int(
            (datetime.now() - timedelta(days=days_to_check)).timestamp())
        end_time = int(datetime.now().timestamp())

        query_id = self.run_insights_query(query, start_time, end_time)
        results = self.poll_insights_query_for_results(query_id)

        email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"

        unique_emails = set()

        for result in results:
            for field in result:
                if field["field"] == "user_name":
                    user_name = field["value"]
                    if re.match(email_regex, user_name):
                        unique_emails.add(user_name.lower())

        return list(unique_emails)
