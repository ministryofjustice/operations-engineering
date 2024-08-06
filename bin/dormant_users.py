import sys
from datetime import datetime
from time import sleep

from dateutil.relativedelta import relativedelta

from config.constants import (MINISTRY_OF_JUSTICE, MISSING_EMAIL_ADDRESS,
                              MOJ_ANALYTICAL_SERVICES)
from config.logging_config import logging
from services.auth0_service import Auth0Service
from services.github_service import GithubService
from services.notify_service import NotifyService
from services.s3_service import S3Service
from services.slack_service import SlackService

MINISTRY_OF_JUSTICE_ALLOW_LIST = [
    "ci-hmcts",
    "cloud-platform-dummy-user",
    "correspondence-tool-bot",
    "form-builder-developers",
    "gecko-moj",
    "hmpps-pcs-tooling",
    "jenkins-moj",
    "laa-machine",
    "mojplatformsdeploy",
    "opg-integrations",
    "opg-use-an-lpa",
    "opg-weblate",
    "slack-moj",
    "sonarqubebot",
    "moj-operations-engineering-bot",
    "operations-engineering-servicenow",
    "laa-service-account",
    "mojanalytics",
    "laaserviceaccount",
    "analytical-platform-bot",
    "hmppsdigitalserviceaccount",
    "hmpps-dso-pr-reviewer",
]

MOJ_ANALYTICAL_SERVICES_ALLOW_LIST = [
]


def convert_str_to_bool(the_string: str | bool) -> bool:
    if the_string in {"True", "true", True}:
        return True
    return False


def get_username(user: dict[str, any]) -> str:
    return user["username"]


def get_allow_list_users(organisation_name: str) -> list[str] | ValueError:
    if organisation_name == MINISTRY_OF_JUSTICE:
        return [user.lower() for user in MINISTRY_OF_JUSTICE_ALLOW_LIST]

    if organisation_name == MOJ_ANALYTICAL_SERVICES:
        return [user.lower() for user in MOJ_ANALYTICAL_SERVICES_ALLOW_LIST]

    raise ValueError(
        f"Unsupported Github Organisation Name [{organisation_name}]")


def get_cli_arguments() -> tuple[str, str, str, str, str, str, str, str, bool, bool, bool, bool] | ValueError:
    expected_number_of_parameters = 13
    if len(sys.argv) != expected_number_of_parameters:
        raise ValueError("Incorrect number of input parameters")

    organisation_name = sys.argv[1]
    admin_github_token = sys.argv[2]
    s3_bucket_name = sys.argv[3]
    slack_token = sys.argv[4]
    notify_token = sys.argv[5]
    auth0_client_secret = sys.argv[6]
    auth0_client_id = sys.argv[7]
    auth0_domain = sys.argv[8]
    debug_mode = convert_str_to_bool(sys.argv[9])
    step_one = convert_str_to_bool(sys.argv[10])
    step_two = convert_str_to_bool(sys.argv[11])
    step_three = convert_str_to_bool(sys.argv[12])
    return organisation_name, admin_github_token, s3_bucket_name, slack_token, notify_token, auth0_client_secret, auth0_client_id, auth0_domain, debug_mode, step_one, step_two, step_three


def get_dormant_users(
    org_members: list,
    organisation_name: str,
    s3_service: S3Service,
    github_service: GithubService,
    auth0_service: Auth0Service,
) -> list:

    if len(org_members) == 0:
        return []

    dormant_users = s3_service.get_users_from_dormant_user_file()
    dormant_users.sort(key=get_username)
    dormant_users = [
        user for user in dormant_users if user["username"] in org_members]
    dormant_users = [user for user in dormant_users if convert_str_to_bool(
        user["is_outside_collaborator"]) is not True]

    allow_list_users = get_allow_list_users(organisation_name)
    dormant_users = [
        user for user in dormant_users if user["username"] not in allow_list_users]

    auth0_active_users = []
    if organisation_name == MINISTRY_OF_JUSTICE:
        auth0_active_users = auth0_service.get_active_users_usernames()
    dormant_users = [user for user in dormant_users if user["username"]
                     not in auth0_active_users]

    org_active_users = s3_service.get_active_users_from_org_people_file()
    dormant_users = [
        user for user in dormant_users if user["username"] not in org_active_users]

    audit_log_active_users = github_service.get_audit_log_active_users(
        dormant_users)
    dormant_users = [user for user in dormant_users if user["username"]
                     not in audit_log_active_users]

    dormant_users.sort(key=get_username)
    return dormant_users


def print_dormant_outside_collaborators(github_service: GithubService, s3_service: S3Service):
    dormant_users = s3_service.get_users_from_dormant_user_file()
    org_outside_collaborators = github_service.get_outside_collaborators_login_names()
    dormant_outside_collaborators = [
        user for user in dormant_users if user["username"] in org_outside_collaborators]
    if len(dormant_outside_collaborators) > 0:
        logging.info("Dormant Outside Collaborators:")
        for user in dormant_outside_collaborators:
            logging.info("\t" + user["username"])


def run_step_one(
    organisation_name: str,
    s3_service: S3Service,
    slack_service: SlackService,
    notify_service: NotifyService,
    github_service: GithubService,
    auth0_service: Auth0Service,
    debug_mode: bool
):

    org_members = github_service.get_org_members_login_names()

    unknown_users_in_allow_list = [
        user for user in get_allow_list_users(organisation_name) if user not in org_members]
    if len(unknown_users_in_allow_list) > 0:
        if debug_mode:
            logging.warning(
                f"Unknown users that need to be removed: {unknown_users_in_allow_list}")
        else:
            slack_service.send_unknown_users_slack_message(
                unknown_users_in_allow_list
            )

    dormant_users = get_dormant_users(
        org_members, organisation_name, s3_service, github_service, auth0_service)

    if len(dormant_users) > 0:
        logging.info("These users are dormant:")

        date_in_one_month = datetime.now() + relativedelta(months=1)

        emailed_users = []
        for user in dormant_users:
            logging.info("\t" + user["username"])
            email_address = github_service.get_user_org_email_address(
                user["username"])

            the_user = {
                "email_address": email_address.lower(),
                "username": user["username"],
                "login_date": date_in_one_month.strftime("%d/%m/%Y"),
                "is_outside_collaborator": False
            }

            if email_address != MISSING_EMAIL_ADDRESS:
                if debug_mode:
                    logging.debug(
                        f"Sending first Notify email to {email_address}")
                else:
                    notify_service.send_first_email(
                        email_address,
                        the_user["login_date"]
                    )
            emailed_users.append(the_user)

        if not debug_mode:
            s3_service.save_emailed_users_file(emailed_users)
            sleep(130)

        undelivered_emails = notify_service.check_for_undelivered_first_emails()
        undelivered_email_addresses = [
            user["email_address"]
            for undelivered_email_user in undelivered_emails
            for user in emailed_users
            if undelivered_email_user["email_address"].lower() == user["email_address"].lower()
        ]

        if len(undelivered_email_addresses) > 0:
            if debug_mode:
                logging.info(
                    f"Undelivered emails: {undelivered_email_addresses}")
            else:
                slack_service.send_undelivered_emails_slack_message(
                    undelivered_email_addresses,
                    organisation_name
                )


def run_step_two(
    organisation_name: str,
    s3_service: S3Service,
    notify_service: NotifyService,
    debug_mode: bool
):
    users_have_emailed = s3_service.get_users_have_emailed()
    allow_list_users = get_allow_list_users(organisation_name)
    users_have_emailed = [
        user for user in users_have_emailed if user["username"] not in allow_list_users]
    users_have_emailed.sort(key=get_username)
    for user in users_have_emailed:
        if (email_address := user['email_address']) != MISSING_EMAIL_ADDRESS:
            if debug_mode:
                logging.debug(
                    f"Sending reminder Notify email to {email_address}")
            else:
                notify_service.send_reminder_email(
                    email_address,
                    user["login_date"]
                )


def run_step_three(
    organisation_name: str,
    s3_service: S3Service,
    slack_service: SlackService,
    notify_service: NotifyService,
    github_service: GithubService,
    auth0_service: Auth0Service,
    debug_mode: bool
):
    org_members = github_service.get_org_members_login_names()

    dormant_users = get_dormant_users(
        org_members, organisation_name, s3_service, github_service, auth0_service)

    users_to_remove = [
        emailed_user
        for emailed_user in s3_service.get_users_have_emailed()
        for dormant_user in dormant_users
        if emailed_user["username"].lower() == dormant_user["username"].lower()
    ]

    if (number_of_users := len(users_to_remove)) > 0:
        logging.info("Users removed from GitHub:")

        for user in users_to_remove:
            logging.info("\t" + user["username"])
            if not debug_mode:
                github_service.remove_user_from_gitub(user["username"])

            if (email_address := user['email_address']) != MISSING_EMAIL_ADDRESS:
                if debug_mode:
                    logging.debug(
                        f"Sending removed Notify email to {email_address}")
                else:
                    notify_service.send_removed_email(
                        email_address
                    )

        if debug_mode:
            logging.debug(
                f"Removed {number_of_users} from {organisation_name} GitHub Organisation")
        else:
            slack_service.send_remove_users_slack_message(
                number_of_users, organisation_name)

    if not debug_mode:
        s3_service.delete_emailed_users_file()


def main():
    logging.info("Start")

    organisation_name, admin_github_token, s3_bucket_name, slack_token, notify_token, auth0_client_secret, auth0_client_id, auth0_domain, debug_mode, step_one, step_two, step_three = get_cli_arguments()

    s3_service = S3Service(s3_bucket_name, organisation_name)
    slack_service = SlackService(slack_token)
    notify_service = NotifyService("", notify_token, organisation_name)
    github_service = GithubService(admin_github_token, organisation_name)
    auth0_service = Auth0Service(
        auth0_client_secret,
        auth0_client_id,
        auth0_domain,
        "client_credentials"
    )

    if step_one:
        print_dormant_outside_collaborators(github_service, s3_service)
        run_step_one(
            organisation_name,
            s3_service,
            slack_service,
            notify_service,
            github_service,
            auth0_service,
            debug_mode
        )

    if step_two:
        run_step_two(organisation_name, s3_service, notify_service, debug_mode)

    if step_three:
        run_step_three(
            organisation_name,
            s3_service,
            slack_service,
            notify_service,
            github_service,
            auth0_service,
            debug_mode
        )

    logging.info("Finished")


if __name__ == "__main__":
    main()
