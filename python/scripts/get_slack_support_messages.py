import os

from python.lib.moj_slack import MojSlack


def main():
    # Config
    days = 30  # Number of days to search back
    channel_id = "C01BUKJSZD4"  # Channel ID of the channel to target

    slack_token = os.getenv("SLACK_BOT_TOKEN")
    if not slack_token:
        raise ValueError(
            "The env variable SLACK_BOT_TOKEN is empty or missing")

    # Setup auth object
    slack_obj = MojSlack(slack_token)

    # Gather all messages from support channel
    all_messages = slack_obj.get_conversation_history(
        channel_id=channel_id, days=days)

    # Filter out unwanted messages
    result = slack_obj.filter_out_subtypes(all_messages)

    # Print out breakdown
    slack_obj.print_breakdown(result, days)

    # Print out total
    print(
        "The definition of a 'message' is a top level message in Slack, this does NOT include threaded messages."
    )
    print(
        "The assumption that only top level messages should count for this use case is that each support request tends to have one message"
    )
    print(
        "And the communication for said request is handed inside the thread for that message"
    )
    print(" ")
    print(f"Total number of messages over the last {days} days: {len(result)}")


if __name__ == "__main__":
    main()
