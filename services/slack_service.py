import logging
import time
from textwrap import dedent
from urllib.parse import quote
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from services.sentry_service import UsageStats


class SlackService:
    OPERATIONS_ENGINEERING_ALERTS_CHANNEL_ID = "C033QBE511V"
    OPERATIONS_ENGINEERING_TEAM_CHANNEL_ID = "CPVD6398C"
    DATE_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
    SENTRY_QUOTA_MANAGEMENT_GUIDANCE = "https://runbooks.operations-engineering.service.justice.gov.uk/documentation/services/sentryio/respond-to-sentry-usage-alert"
    OPERATION_ENGINEERING_REPOSITORY_URL = "https://github.com/ministryofjustice/operations-engineering"

    # Added to stop TypeError on instantiation. See https://github.com/python/cpython/blob/d2340ef25721b6a72d45d4508c672c4be38c67d3/Objects/typeobject.c#L4444
    def __new__(cls, *args, **kwargs):
        return super(SlackService, cls).__new__(cls)

    def __init__(self, slack_token: str) -> None:
        self.slack_client = WebClient(slack_token)

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

    def send_slack_support_stats_report(self, support_statistics):
        message = (
            f"*Slack Support Stats Report*\n\n"
            f"Here an overview of our recent support statistics:\n"
            f"{support_statistics}"
        )
        blocks = self._create_block_with_message(message)
        self._send_alert_to_operations_engineering(blocks)

    def send_dormant_user_list(self, user_list):
        message = (
            f"*Dormant User Report*\n\n"
            f"Here is a list of dormant GitHub users that have not been seen in Auth0 logs:\n"
            f"{user_list}"
        )
        blocks = self._create_block_with_message(message)
        self._send_alert_to_operations_engineering(blocks)

    def send_pat_report_alert(self):
        message = (
            "*Expired PAT Report*\n\n"
            "Some expired PAT(s) have been detected.\n\n"
            "Please review the current list here:\n"
            "https://github.com/organizations/ministryofjustice/settings/personal-access-tokens/active"
        )
        blocks = self._create_block_with_message(message)
        self._send_alert_to_operations_engineering(blocks)

    def send_new_github_joiner_metrics_alert(self, new_members_added_by_oe, new_members_added_externally, percentage, total_new_members, org, audit_log_url, time_delta_in_days):
        message = (
            f"*GitHub Joiner Metrics*\n\n"
            f"Here are the {total_new_members} new joiners added in the last {time_delta_in_days} days within the '{org}' GitHub org. \n\n"
            f"*Added by Operations Engineering:*\n"
            f"{new_members_added_by_oe}\n\n"
            f"*Added externally:*\n"
            f"{new_members_added_externally}\n\n"
            f"{percentage}% of the new joiners were added by operations engineering.\n\n"
            f"Please review the audit log for more details: {audit_log_url}"
        )
        blocks = self._create_block_with_message(message)
        self._send_alert_to_operations_engineering(blocks)

    def send_new_github_owners_alert(self, new_owner, date_added, added_by, org, audit_log_url):
        message = (
            f"*New GitHub Owners Detected*\n\n"
            f"A new owner has been detected in the `{org}` GitHub org.\n\n"
            f"*New owner:* {new_owner}\n"
            f"*Date added:* {date_added}\n"
            f"*By who:* {added_by}\n\n"
            f"Please review the audit log for more details: {audit_log_url}"
        )
        blocks = self._create_block_with_message(message)
        self._send_alert_to_operations_engineering(blocks)

    def send_low_github_licenses_alert(self, remaining_licenses):
        message = (
            f"*Low GitHub Licenses Remaining*\n\n"
            f"There are only {remaining_licenses} GitHub licenses remaining in the enterprise account.\n\n"
            f"Please add more licenses using the instructions outlined here:"
            f"https://runbooks.operations-engineering.service.justice.gov.uk/documentation/internal/low-github-seats-procedure.html"
        )
        blocks = self._create_block_with_message(message)
        self._send_alert_to_operations_engineering(blocks)

    def send_low_github_actions_quota_alert(self, percentage_used):
        message = (
            f"*Low GitHub Actions Quota*\n\n"
            f"{round(100 - percentage_used, 1)}% of the Github Actions minutes quota remains.\n"
            f"What to do next: https://runbooks.operations-engineering.service.justice.gov.uk/documentation/internal/low-github-actions-minutes-procedure.html#low-github-actions-minutes-procedure"
        )
        blocks = self._create_block_with_message(message)
        self._send_alert_to_operations_engineering(blocks)

    def send_low_gandi_funds_alert(self, remaining_funds, threshold):
        message = (
            f"*Low Gandi Funds Remaining*\n\n"
            f":warning: We currently have £{remaining_funds} left out of £{threshold}\n\n"
            f"Please read the following Runbook for next steps:"
            f"https://runbooks.operations-engineering.service.justice.gov.uk/documentation/certificates/manual-ssl-certificate-processes.html#regenerating-certificates"
        )
        blocks = self._create_block_with_message(message)
        self._send_alert_to_operations_engineering(blocks)

    def send_unknown_user_alert_to_operations_engineering(self, users: list):
        message = (
            f"*Dormant Users Automation*\n\n"
            f"Remove these users from the Dormant Users allow list:\n"
            f"{users}"
        )
        blocks = self._create_block_with_message(message)
        self._send_alert_to_operations_engineering(blocks)

    def send_remove_users_from_github_alert_to_operations_engineering(
        self, number_of_users: int, organisation_name: str
    ):
        message = (
            f"*Dormant Users Automation*\n\n"
            f"Removed {number_of_users} users from the {organisation_name} GitHub Organisation.\n\n"
            f"See the GH Action for more info: {self.OPERATION_ENGINEERING_REPOSITORY_URL}"
        )
        blocks = self._create_block_with_message(message)
        self._send_alert_to_operations_engineering(blocks)

    def send_unused_circleci_context_alert_to_operations_engineering(self, number_of_contexts: int):
        message = (
            f"*Unused CircleCI Contexts*\n\n"
            f"A total of {number_of_contexts} unused CircleCI contexts have been detected.\n\n"
            f"Please see the GH Action for more information: {self.OPERATION_ENGINEERING_REPOSITORY_URL}"
        )
        blocks = self._create_block_with_message(message)
        self._send_alert_to_operations_engineering(blocks)

    def send_undelivered_email_alert_to_operations_engineering(
        self, email_addresses: list, organisation_name: str
    ):
        message = (
            f"*Dormant Users Automation*\n\n"
            f"Undelivered emails for {organisation_name} GitHub Organisation:\n"
            f"{email_addresses}\n\n"
            f"Remove these users manually."
        )
        blocks = self._create_block_with_message(message)
        self._send_alert_to_operations_engineering(blocks)

    def send_unowned_repos_slack_message(self, repositories: list):
        message = (
            f"*Unowned Repositories Automation*\n\n"
            f"Repositories on the GitHub Organisation that have no team or collaborator:\n"
            f"{repositories}"
        )
        blocks = self._create_block_with_message(message)
        self._send_alert_to_operations_engineering(blocks)

    def send_remove_users_slack_message(self, number_of_users: int, organisation_name: str):
        message = f"*Dormant Users Automation*\nRemoved {number_of_users} users from the {organisation_name} GitHub Organisation.\nSee the GH Action for more info: {self.OPERATION_ENGINEERING_REPOSITORY_URL}"
        blocks = self._create_block_with_message(message)
        self._send_alert_to_operations_engineering(blocks)

    def send_unknown_users_slack_message(self, unknown_users: list):
        message = f"*Dormant Users Automation*\nRemove these users from the Dormant Users allow list:\n{unknown_users}"
        blocks = self._create_block_with_message(message)
        self._send_alert_to_operations_engineering(blocks)

    def send_undelivered_emails_slack_message(self, email_addresses: list, organisation_name: str):
        message = f"*Dormant Users Automation*\nUndelivered emails for {organisation_name} GitHub Organisation:\n{email_addresses}\nRemove these users manually"
        blocks = self._create_block_with_message(message)
        self._send_alert_to_operations_engineering(blocks)

    def _send_alert_to_operations_engineering(self, blocks: list[dict]):
        try:
            self.slack_client.chat_postMessage(
                channel=self.OPERATIONS_ENGINEERING_ALERTS_CHANNEL_ID,
                mrkdown=True,
                blocks=blocks
            )
        except SlackApiError as e:
            logging.error("Slack API error: {%s}", e.response['error'])
        except Exception as e:
            logging.error("Failed to send Slack alert: {%s}", str(e))

    def _create_block_with_message(self, message, block_type="section"):
        return [
            {
                "type": block_type,
                "text": {
                    "type": "mrkdwn",
                    "text": message
                }
            }
        ]

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
