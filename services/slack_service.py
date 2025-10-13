# pylint: disable=C0411, R0917

import logging
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


class SlackService:
    OPERATIONS_ENGINEERING_ALERTS_CHANNEL_ID = "C033QBE511V"
    OPERATIONS_ENGINEERING_TEAM_CHANNEL_ID = "CPVD6398C"
    DATE_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
    OPERATION_ENGINEERING_REPOSITORY_URL = "https://github.com/ministryofjustice/operations-engineering"

    # Added to stop TypeError on instantiation. See https://github.com/python/cpython/blob/d2340ef25721b6a72d45d4508c672c4be38c67d3/Objects/typeobject.c#L4444
    def __new__(cls, *args, **kwargs):
        return super(SlackService, cls).__new__(cls)

    def __init__(self, slack_token: str) -> None:
        self.slack_client = WebClient(slack_token)

    def send_slack_support_stats_report(self, support_statistics):
        message = (
            f"*Slack Support Stats Report*\n\n"
            f"Here an overview of our recent support statistics:\n"
            f"{support_statistics}"
        )
        blocks = self._create_block_with_message(message)
        self._send_alert_to_operations_engineering(blocks)

    def send_dormant_user_list(self, user_list, days_since: str):
        message = (
            f"*Dormant User Report*\n\n"
            f"Here is a list of dormant GitHub users that have not been seen in Auth0 logs for {days_since} days:\n"
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

    def send_alert_for_poc_repositories(self, repositories):
        message = (
            "The following POC GitHub Repositories persist:\n\n"
            + "\n".join([f"https://github.com/ministryofjustice/{repo} - {age} days old" for repo, age in repositories.items()])
            + "\n\nConsider if they are still required. If not, please archive them by removing them from the Terraform configuration: https://github.com/ministryofjustice/operations-engineering/tree/main/terraform/github/repositories/ministryofjustice"
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

    def send_github_rejoin_report(self, total_removed_moj, total_rejoined_moj, error_rate_moj):
        message = (
            f"*Erroneous User Removal Report*\n\n"
            f"Over the past week:\n\n"
            f"We have removed {total_removed_moj} users, with {total_rejoined_moj} since rejoining.\n\n"
            f"Our erroneous removal rate for users is {error_rate_moj}%."
        )
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
