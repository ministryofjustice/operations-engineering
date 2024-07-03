import logging
import time
from textwrap import dedent
from urllib.parse import quote

from slack_sdk import WebClient

from services.sentry_service import UsageStats


class SlackService:
    OPERATIONS_ENGINEERING_ALERTS_CHANNEL_ID = "C033QBE511V"
    OPERATIONS_ENGINEERING_TEAM_CHANNEL_ID = "CPVD6398C"
    DATE_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
    SENTRY_QUOTA_MANAGEMENT_GUIDANCE = "https://runbooks.operations-engineering.service.justice.gov.uk/documentation/services/sentryio/respond-to-sentry-usage-alert"

    # Added to stop TypeError on instantiation. See https://github.com/python/cpython/blob/d2340ef25721b6a72d45d4508c672c4be38c67d3/Objects/typeobject.c#L4444
    def __new__(cls, *args, **kwargs):
        return super(SlackService, cls).__new__(cls)

    def __init__(self, slack_token: str) -> None:
        self.slack_client = WebClient(slack_token)

    def send_message_to_plaintext_channel_name(self, message, channel_name: str):
        """
        Sends a message to a plaintext channel by name.

        Args:
            message (str): The message to send.
            channel_name (str): The name of the channel to send the message to.
        """
        channel_id = self._lookup_channel_id(channel_name)
        if channel_id is None:
            logging.error("Could not find channel %s", channel_name)
        else:
            response = self.slack_client.chat_postMessage(
                channel=channel_id, text=message)
            if not response['ok']:
                logging.error("Error sending message to channel %s: %s",
                              channel_name, response['error'])
            else:
                logging.info("Message sent to channel %s", channel_name)

    def _lookup_channel_id(self, channel_name, cursor=''):
        channel_id = None
        response = self.slack_client.conversations_list(
            limit=200, cursor=cursor)

        if response['channels'] is not None:
            for channel in response['channels']:
                if channel['name'] == channel_name:
                    channel_id = channel['id']
                    break

        if channel_id is None and response['response_metadata']['next_cursor'] != '':
            channel_id = self._lookup_channel_id(
                channel_name, cursor=response['response_metadata']['next_cursor'])

        return channel_id

    def send_usage_alert_to_operations_engineering(
        self, period_in_days: int, usage_stats: UsageStats, usage_threshold: float, category: str
    ):
        category_lower = category.lower()
        category_capitalised = category.capitalize()
        self.slack_client.chat_postMessage(
            channel=self.OPERATIONS_ENGINEERING_ALERTS_CHANNEL_ID,
            mrkdown=True,
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": dedent(f"""
                            :warning: *Sentry {category_capitalised} Usage Alert :sentry::warning:*
                            - Usage threshold: {usage_threshold:.0%}
                            - Period: {period_in_days} {'days' if period_in_days > 1 else 'day'}
                            - Max usage for period: {usage_stats.max_usage} {category_capitalised}s
                            - {category_capitalised}s consumed over period: {usage_stats.total}
                            - Percentage consumed: {usage_stats.percentage_of_quota_used:.0%}
                        """).strip("\n")
                    }
                },
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"Check Sentry for projects with excessive {category_lower}s :eyes:"
                    },
                    "accessory": {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": f":sentry: {category_capitalised} usage for period",
                            "emoji": True
                        },
                        "url": f"https://ministryofjustice.sentry.io/stats/?dataCategory={category_lower}s&end={quote(usage_stats.end_time.strftime(self.DATE_FORMAT))}&sort=-accepted&start={quote(usage_stats.start_time.strftime(self.DATE_FORMAT))}&utc=true"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "See Sentry usage alert runbook for help with this alert"
                    },
                    "accessory": {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": ":blue_book: Runbook",
                            "emoji": True
                        },
                        "url": self.SENTRY_QUOTA_MANAGEMENT_GUIDANCE
                    }
                }
            ]
        )

    def send_unknown_user_alert_to_operations_engineering(self, users: list):
        self.slack_client.chat_postMessage(
            channel=self.OPERATIONS_ENGINEERING_ALERTS_CHANNEL_ID,
            mrkdown=True,
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": dedent(f"""
                            *Dormants Users Automation*
                            Remove these users from the Dormants Users allow list:
                            {users}
                        """).strip("\n")
                    }
                }
            ]
        )

    def send_remove_users_from_github_alert_to_operations_engineering(
        self, number_of_users: int, organisation_name: str
    ):
        self.slack_client.chat_postMessage(
            channel=self.OPERATIONS_ENGINEERING_ALERTS_CHANNEL_ID,
            mrkdown=True,
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": dedent(f"""
                            *Dormants Users Automation*
                            Removed {number_of_users} users from the {organisation_name} GitHub Organisation.
                            See the GH Action for more info: https://github.com/ministryofjustice/operations-engineering
                        """).strip("\n")
                    }
                }
            ]
        )

    def send_unused_circleci_context_alert_to_operations_engineering(self, number_of_contexts: int):
        self.slack_client.chat_postMessage(
            channel=self.OPERATIONS_ENGINEERING_ALERTS_CHANNEL_ID,
            mrkdown=True,
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": dedent(f"""
                            *Unused CircleCI Contexts*
                            A total of {number_of_contexts} unused CircleCI contexts have been detected.
                            Please see the GH Action for more information: https://github.com/ministryofjustice/operations-engineering
                        """).strip("\n")
                    }
                }
            ]
        )

    def send_undelivered_email_alert_to_operations_engineering(
        self, email_addresses: list, organisation_name: str
    ):
        self.slack_client.chat_postMessage(
            channel=self.OPERATIONS_ENGINEERING_ALERTS_CHANNEL_ID,
            mrkdown=True,
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": dedent(f"""
                            *Dormants Users Automation*
                            Undelivered emails for {organisation_name} GitHub Organisation:
                            {email_addresses}
                            Remove these users manually
                        """).strip("\n")
                    }
                }
            ]
        )

    def send_remove_users_slack_message(self, number_of_users: int, organisation_name: str):
        message = f"*Dormants Users Automation*\nRemoved {number_of_users} users from the {organisation_name} GitHub Organisation.\nSee the GH Action for more info: https://github.com/ministryofjustice/operations-engineering"
        blocks = self._create_block_with_message(message)
        self._send_alert_to_operations_engineering(blocks)

    def send_unknown_users_slack_message(self, unknown_users: list):
        message = f"*Dormants Users Automation*\nRemove these users from the Dormants Users allow list:\n{unknown_users}"
        blocks = self._create_block_with_message(message)
        self._send_alert_to_operations_engineering(blocks)

    def send_undelivered_emails_slack_message(self, email_addresses: list, organisation_name: str):
        message = f"*Dormants Users Automation*\nUndelivered emails for {organisation_name} GitHub Organisation:\n{email_addresses}\nRemove these users manually"
        blocks = self._create_block_with_message(message)
        self._send_alert_to_operations_engineering(blocks)

    def _send_alert_to_operations_engineering(self, blocks: list[dict]):
        self.slack_client.chat_postMessage(channel=self.OPERATIONS_ENGINEERING_ALERTS_CHANNEL_ID,
                                           mrkdown=True,
                                           blocks=blocks
                                           )

    def _create_block_with_message(self, message):
        return [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": message
                }
            }
        ]

    def send_unowned_repos_slack_message(self, repositories: list):
        self.slack_client.chat_postMessage(
            channel=self.OPERATIONS_ENGINEERING_ALERTS_CHANNEL_ID,
            mrkdown=True,
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": dedent(f"""
                            *Unowned Repositories Automation*
                            Repositories on the GitHub Organisation that have no team or collaborator:
                            {repositories}
                        """).strip("\n")
                    }
                }
            ]
        )

    def get_all_slack_usernames(self):
        """Fetches all usernames and user email addresses from the Slack API.

        Returns:
            user_data: A list of of JSON objects
        """

        user_data = []
        cursor = None
        limit = 200
        delay_seconds = 1

        try:
            while True:
                response = self.slack_client.users_list(
                    cursor=cursor, limit=limit)

                if response['ok']:
                    for user in response['members']:

                        email = user['profile'].get('email')

                        if email is None:
                            continue

                        user_info = {
                            "username": user['name'],
                            "email": email
                        }
                        user_data.append(user_info)

                    cursor = response.get(
                        'response_metadata', {}).get('next_cursor')
                    if not cursor:
                        break
                else:
                    logging.error("Error fetching user data: %s}",
                                  response['error'])
                    break
                time.sleep(delay_seconds)
        except Exception as e:
            logging.error("An error has occurred connecting to Slack: %s", e)
            return []

        return user_data
