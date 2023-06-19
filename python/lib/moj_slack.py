import logging
from time import sleep
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from datetime import datetime, timedelta


class MojSlack:

    # Logging Config
    logging.basicConfig(
        format="%(asctime)s %(levelname)-8s %(message)s",
        level=logging.INFO,
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    def __init__(self, slack_token: str) -> None:
        self.client = WebClient(slack_token)



    
    def get_conversation_history(self, channel_id, days):
        """This method returns a list of all messages sent in a target Slack channel over the past X days

        Args:
            channel_id (str): Slack channel ID - this can be retrieved from the URL in Slack Web
            days (int): How long you want to search back

        Returns:
            list[dict]: Returns a list of dicts, each dict entry contains a Slack message
        """
        try:

            # Setup args for API call
            args = {
                "channel": channel_id,
                "oldest": self.generate_datetime(days),
                "include_all_metadata": False,
                "limit": 100,
                "has_more": True,
            }

            # Prepare list for final list of messages
            messages = list()

            # Paginate until all results gathered
            while args["has_more"]:
                # Slow down for rate limit
                sleep(1)

                # Continue calling API using pagination
                response = self.client.conversations_history(**args)

                # Check if any more record pages
                args["has_more"] = True if response["has_more"] else False
                args["cursor"] = (
                    response["response_metadata"]["next_cursor"]
                    if response["has_more"]
                    else None
                )

                # Append new messages to list
                messages += response["messages"]

            return messages
        except SlackApiError as e:
            self.print_slack_error(e, "test")

    def print_slack_error(self, slack_error, function) -> None:
        """Print error from Slack API usage

        Args:
            slack_error (SlackApiError): https://slack.dev/python-slack-sdk/api-docs/slack_sdk/errors/index.html
            function (str): Function name the error was detected
        """

        assert slack_error.response["ok"] is False
        assert slack_error.response["error"]

        logging.error("Got an Error calling Slack API")
        logging.error(f"Function: {function}")
        logging.error(f"Error: {slack_error}")

    # This is quite inefficient/hacky but does seem to run fast enough - room for optimisation at a later day
    # When we decide what we want to do with this data, this is enough to just print for now

    @staticmethod
    def print_breakdown(list_of_messages, days) -> None:
        """This method takes a list of Slack messages and a number of days to search back, it will print how many messages in that list
        Are from each day.

        Args:
            list_of_messages (list[dict]): A list of Slack messages
            days (int): How many days to search back
        """
        # Loop from today to X days ago
        for day in range(0, days - 1):

            # Get the date object for the day
            date = (datetime.now() - timedelta(day)).date()

            # Store how many messages are from that day
            running_count = 0

            # Check and add to running count if its from the same day
            for message in list_of_messages:
                if date == datetime.fromtimestamp(float(message["ts"])).date():
                    running_count += 1

            # Print the results - need to work out what we want to do with them before adding more functionality
            # Not using logging to make it easier to copy paste
            print(date)
            print(running_count)

    @staticmethod
    def generate_datetime(number_of_days) -> float:
        """Generates a epoch timestamp from a number of days in the past

        Example: passing number_of_days = 30, will return the epoch for 30 days ago

        Args:
            number_of_days (int): number of days in the past you want the epoch date for

        Returns:
            float: epoch timestamp for (today - number_of_days)
        """

        return (datetime.now() - timedelta(number_of_days)).timestamp()

    @staticmethod
    def filter_out_subtypes(list_of_messages):
        """This function filters out all messages from a list of Slack messages which contain the key subtype.
        This is needed as messages with that key are not real messages (they tend to be bots)

        Args:
            list_of_messages (list[dict]): a list of dict objects containing Slack messages - get_conversation_history can return this

        Returns:
            list[dict]:  a list of dict objects containing Slack messages with all entries containing the key subtype filtered out
        """
        return list(filter(lambda x: ("subtype" not in x), list_of_messages))
