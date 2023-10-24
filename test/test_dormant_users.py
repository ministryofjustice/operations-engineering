import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
from freezegun import freeze_time
from config.constants import MISSING_EMAIL_ADDRESS

from scripts.dormant_users import (
    main,
    convert_str_to_bool,
    get_username,
    get_allow_list_users,
    get_cli_arguments,
    print_dormant_outside_collaborators,
    run_step_one,
    run_step_two,
    run_step_three,
    get_dormant_users,
    MINISTRY_OF_JUSTICE_ALLOW_LIST,
    MOJ_ANALYTICAL_SERVICES_ALLOW_LIST,
)

from config.constants import (
    MINISTRY_OF_JUSTICE,
    MOJ_ANALYTICAL_SERVICES,
)

# pylint: disable=W0611 W0613


def create_undelivered_email_user(email_address):
    return {
        "email_address": email_address,
        "created_at": datetime.now().strftime("%d/%m/%Y"),
        "status": "failed"
    }


def create_saved_json_file_user(username):
    return {
        "email_address": "some-email",
        "username": username,
        "login_date": datetime.now().strftime("%d/%m/%Y"),
        "is_outside_collaborator": False
    }


def create_dormant_file_user(username):
    return {
        "username": username,
        "is_outside_collaborator": False
    }


@patch("python.scripts.dormant_users.GithubService", new=MagicMock)
@patch("python.scripts.dormant_users.S3Service", new=MagicMock)
@patch("python.scripts.dormant_users.SlackService", new=MagicMock)
@patch("python.scripts.dormant_users.NotifyService", new=MagicMock)
@patch("python.scripts.dormant_users.Auth0Service", new=MagicMock)
@patch("python.scripts.dormant_users.run_step_one")
@patch("python.scripts.dormant_users.run_step_two")
@patch("python.scripts.dormant_users.run_step_three")
@patch("python.scripts.dormant_users.print_dormant_outside_collaborators")
class TestDormantUsersMain(unittest.TestCase):

    @patch("sys.argv", ["", "", "", "", "", "", "", "", "", "", "true", "", ""])
    def test_main_runs_step_one(self, mock_print, mock_run_step_three, mock_run_step_two, mock_run_step_one):
        main()
        mock_print.assert_called_once()
        mock_run_step_one.assert_called_once()
        mock_run_step_two.assert_not_called()
        mock_run_step_three.assert_not_called()

    @patch("sys.argv", ["", "", "", "", "", "", "", "", "", "", "", "true", ""])
    def test_main_runs_step_two(self, mock_print, mock_run_step_three, mock_run_step_two, mock_run_step_one):
        main()
        mock_run_step_one.assert_not_called()
        mock_print.assert_not_called()
        mock_run_step_two.assert_called_once()
        mock_run_step_three.assert_not_called()

    @patch("sys.argv", ["", "", "", "", "", "", "", "", "", "", "", "", "true"])
    def test_main_runs_step_three(self, mock_print, mock_run_step_three, mock_run_step_two, mock_run_step_one):
        main()
        mock_run_step_one.assert_not_called()
        mock_print.assert_not_called()
        mock_run_step_two.assert_not_called()
        mock_run_step_three.assert_called_once()


class TestDormantUsers(unittest.TestCase):

    def setUp(self):
        self.user = create_dormant_file_user("some-user")

    def test_convert_str_to_bool(self):
        self.assertEqual(convert_str_to_bool("True"), True)
        self.assertEqual(convert_str_to_bool("true"), True)
        self.assertEqual(convert_str_to_bool(True), True)
        self.assertEqual(convert_str_to_bool("False"), False)
        self.assertEqual(convert_str_to_bool("false"), False)

    def test_get_username(self):
        the_dict = {"username": "some-user"}
        self.assertEqual("some-user", get_username(the_dict))

    def test_get_allow_list_users(self):
        self.assertEqual(get_allow_list_users(
            MINISTRY_OF_JUSTICE), MINISTRY_OF_JUSTICE_ALLOW_LIST)
        self.assertEqual(get_allow_list_users(
            MOJ_ANALYTICAL_SERVICES), MOJ_ANALYTICAL_SERVICES_ALLOW_LIST)

    def test_get_allow_list_users_raise_error(self):
        self.assertRaises(
            ValueError, get_allow_list_users, "some-org")

    @patch("sys.argv", ["", "", "", "", "", "", "", "", "", "", "", "", ""])
    def test_get_cli_arguments_correct_length(self):
        args = get_cli_arguments()
        self.assertEqual(len(args), 12)

    @patch("sys.argv", [""])
    def test_get_cli_arguments_raises_error(self):
        self.assertRaises(
            ValueError, get_cli_arguments)

    @patch("python.services.s3_service.S3Service")
    @patch("python.services.github_service.GithubService")
    def test_print_dormant_outside_collaborators_path(self, mock_github_service, mock_s3_service):
        mock_s3_service.get_users_from_dormant_user_file.return_value = [
            self.user]
        mock_github_service.get_outside_collaborators_login_names.return_value = [
            self.user["username"]]
        print_dormant_outside_collaborators(
            mock_github_service, mock_s3_service)

    @patch("python.services.s3_service.S3Service")
    @patch("python.services.github_service.GithubService")
    def test_print_dormant_outside_collaborators_no_users(self, mock_github_service, mock_s3_service):
        mock_s3_service.get_users_from_dormant_user_file.return_value = []
        mock_github_service.get_outside_collaborators_login_names.return_value = []
        print_dormant_outside_collaborators(
            mock_github_service, mock_s3_service)


@patch("python.services.auth0_service.Auth0Service")
@patch("python.services.s3_service.S3Service")
@patch("python.services.github_service.GithubService")
class TestGetDormantUsers(unittest.TestCase):
    def test_get_dormant_users_when_no_users_in_file(self, mock_github_service, mock_s3_service, mock_auth0_service):
        org_users = []
        dormant_users = get_dormant_users(
            org_users,
            MINISTRY_OF_JUSTICE,
            mock_s3_service,
            mock_github_service,
            mock_auth0_service
        )

        self.assertEqual(len(dormant_users), 0)

    def test_get_dormant_users_when_not_moj(self, mock_github_service, mock_s3_service, mock_auth0_service):
        mock_s3_service.get_users_from_dormant_user_file.return_value = [
            create_dormant_file_user("dormant-user"),
            create_dormant_file_user("moj-operations-engineering-bot"),
            create_dormant_file_user("other-org-user"),
            create_dormant_file_user("full-org-user"),
            create_dormant_file_user("active-auth0-user"),
            create_dormant_file_user("active-org-file-user"),
            create_dormant_file_user("active-audit-log-user"),
            {
                "username": "collab-user",
                "is_outside_collaborator": True
            }
        ]

        mock_s3_service.get_active_users_from_org_people_file.return_value = [
            "active-org-file-user"]
        mock_github_service.get_audit_log_active_users.return_value = [
            "active-audit-log-user"]

        org_users = [
            create_dormant_file_user("some-user"),
            "dormant-user",
            "moj-operations-engineering-bot",
            "active-auth0-user",
            "active-org-file-user",
            "active-audit-log-user",
            "collab-user"
        ]

        dormant_users = get_dormant_users(
            org_users,
            MOJ_ANALYTICAL_SERVICES,
            mock_s3_service,
            mock_github_service,
            mock_auth0_service
        )

        mock_auth0_service.get_active_users_usernames.assert_not_called()
        self.assertEqual(len(dormant_users), 3)

    def test_get_dormant_users_when_moj_org(self, mock_github_service, mock_s3_service, mock_auth0_service):
        mock_s3_service.get_users_from_dormant_user_file.return_value = [
            create_dormant_file_user("dormant-user"),
            create_dormant_file_user("moj-operations-engineering-bot"),
            create_dormant_file_user("other-org-user"),
            create_dormant_file_user("full-org-user"),
            create_dormant_file_user("active-auth0-user"),
            create_dormant_file_user("active-org-file-user"),
            create_dormant_file_user("active-audit-log-user"),
            {
                "username": "collab-user",
                "is_outside_collaborator": True
            }
        ]

        mock_auth0_service.get_active_users_usernames.return_value = [
            "active-auth0-user"]
        mock_s3_service.get_active_users_from_org_people_file.return_value = [
            "active-org-file-user"]
        mock_github_service.get_audit_log_active_users.return_value = [
            "active-audit-log-user"]

        org_users = [
            create_dormant_file_user("some-user"),
            "dormant-user",
            "moj-operations-engineering-bot",
            "active-auth0-user",
            "active-org-file-user",
            "active-audit-log-user",
            "collab-user"
        ]

        dormant_users = get_dormant_users(
            org_users,
            MINISTRY_OF_JUSTICE,
            mock_s3_service,
            mock_github_service,
            mock_auth0_service
        )

        self.assertEqual(len(dormant_users), 1)


@patch("python.services.auth0_service.Auth0Service")
@patch("python.services.s3_service.S3Service")
@patch("python.services.github_service.GithubService")
@patch("python.services.notify_service.NotifyService")
@patch("python.services.slack_service.SlackService")
@patch("python.scripts.dormant_users.get_dormant_users")
class TestRunStepOne(unittest.TestCase):
    def test_run_step_one_in_production_mode_when_no_dormant_users_find_unknown_user(self, mock_get_dormant_users, mock_slack_service, mock_notify_service, mock_github_service, mock_s3_service, mock_auth0_service):
        mock_github_service.get_org_members_login_names.return_value = []
        mock_get_dormant_users.return_value = []
        run_step_one(
            MINISTRY_OF_JUSTICE,
            mock_s3_service,
            mock_slack_service,
            mock_notify_service,
            mock_github_service,
            mock_auth0_service,
            False
        )
        mock_slack_service.send_unknown_users_slack_message.assert_called_once_with(
            MINISTRY_OF_JUSTICE_ALLOW_LIST)
        mock_notify_service.send_first_email.assert_not_called()
        mock_s3_service.save_emailed_users_file.assert_not_called()
        mock_slack_service.send_undelivered_emails_slack_message.assert_not_called()

    def test_run_step_one_in_debug_mode_when_no_dormant_users(self, mock_get_dormant_users, mock_slack_service, mock_notify_service, mock_github_service, mock_s3_service, mock_auth0_service):
        mock_github_service.get_org_members_login_names.return_value = [
            "full-org-user"]
        mock_get_dormant_users.return_value = []
        run_step_one(
            MINISTRY_OF_JUSTICE,
            mock_s3_service,
            mock_slack_service,
            mock_notify_service,
            mock_github_service,
            mock_auth0_service,
            True
        )
        mock_slack_service.send_unknown_users_slack_message.assert_not_called()
        mock_notify_service.send_first_email.assert_not_called()
        mock_s3_service.save_emailed_users_file.assert_not_called()
        mock_slack_service.send_undelivered_emails_slack_message.assert_not_called()

    @freeze_time("2023-07-13")
    def test_run_step_one_in_debug_mode(self, mock_get_dormant_users, mock_slack_service, mock_notify_service, mock_github_service, mock_s3_service, mock_auth0_service):
        mock_github_service.get_org_members_login_names.return_value = [
            "full-org-user"]
        user = create_saved_json_file_user("full-org-user")
        mock_get_dormant_users.return_value = [user]
        mock_notify_service.check_for_undelivered_first_emails.return_value = [
            create_undelivered_email_user("some-email")]
        mock_github_service.get_user_org_email_address.return_value = "some-email"

        run_step_one(
            MINISTRY_OF_JUSTICE,
            mock_s3_service,
            mock_slack_service,
            mock_notify_service,
            mock_github_service,
            mock_auth0_service,
            True
        )
        mock_slack_service.send_unknown_users_slack_message.assert_not_called()
        mock_notify_service.send_first_email.assert_not_called()
        mock_s3_service.save_emailed_users_file.assert_called_once_with(
            [{"email_address": "some-email", "username": "full-org-user", "login_date": "13/08/2023", "is_outside_collaborator": False}])
        mock_slack_service.send_undelivered_emails_slack_message.assert_not_called()

    @freeze_time("2023-07-13")
    def test_run_step_one_when_user_missing_email_address(self, mock_get_dormant_users, mock_slack_service, mock_notify_service, mock_github_service, mock_s3_service, mock_auth0_service):
        mock_github_service.get_org_members_login_names.return_value = [
            "full-org-user"]
        user = create_saved_json_file_user("full-org-user")
        mock_get_dormant_users.return_value = [user]
        mock_notify_service.check_for_undelivered_first_emails.return_value = [
            create_undelivered_email_user("some-email")]
        mock_github_service.get_user_org_email_address.return_value = MISSING_EMAIL_ADDRESS

        run_step_one(
            MINISTRY_OF_JUSTICE,
            mock_s3_service,
            mock_slack_service,
            mock_notify_service,
            mock_github_service,
            mock_auth0_service,
            True
        )
        mock_slack_service.send_unknown_users_slack_message.assert_not_called()
        mock_notify_service.send_first_email.assert_not_called()
        mock_s3_service.save_emailed_users_file.assert_called_once_with(
            [{"email_address": MISSING_EMAIL_ADDRESS, "username": "full-org-user", "login_date": "13/08/2023", "is_outside_collaborator": False}])
        mock_slack_service.send_undelivered_emails_slack_message.assert_not_called()

    @freeze_time("2023-08-13")
    @patch("python.scripts.dormant_users.sleep", return_value=None)
    def test_run_step_one_in_production_mode(self, mock_sleep, mock_get_dormant_users, mock_slack_service, mock_notify_service, mock_github_service, mock_s3_service, mock_auth0_service):
        new_list = MINISTRY_OF_JUSTICE_ALLOW_LIST.copy()
        mock_github_service.get_org_members_login_names.return_value = new_list
        user = create_saved_json_file_user("full-org-user")
        mock_get_dormant_users.return_value = [user]
        mock_notify_service.check_for_undelivered_first_emails.return_value = [
            create_undelivered_email_user("some-email")]
        mock_github_service.get_user_org_email_address.return_value = "some-email"

        run_step_one(
            MINISTRY_OF_JUSTICE,
            mock_s3_service,
            mock_slack_service,
            mock_notify_service,
            mock_github_service,
            mock_auth0_service,
            False
        )
        mock_slack_service.send_unknown_users_slack_message.assert_not_called()
        mock_notify_service.send_first_email.assert_called_once_with(
            "some-email", "13/09/2023")
        mock_s3_service.save_emailed_users_file.assert_called_once_with(
            [{"email_address": "some-email", "username": "full-org-user", "login_date": "13/09/2023", "is_outside_collaborator": False}])
        mock_slack_service.send_undelivered_emails_slack_message.assert_called_once_with(
            ["some-email"], MINISTRY_OF_JUSTICE)

    @freeze_time("2023-08-13")
    @patch("python.scripts.dormant_users.sleep", return_value=None)
    def test_run_step_one_in_production_mode_with_no_undelivered_email(self, mock_sleep, mock_get_dormant_users, mock_slack_service, mock_notify_service, mock_github_service, mock_s3_service, mock_auth0_service):
        mock_github_service.get_org_members_login_names.return_value = MINISTRY_OF_JUSTICE_ALLOW_LIST
        user = create_saved_json_file_user("full-org-user")
        mock_get_dormant_users.return_value = [user]
        mock_notify_service.check_for_undelivered_first_emails.return_value = []
        mock_github_service.get_user_org_email_address.return_value = "some-email"

        run_step_one(
            MINISTRY_OF_JUSTICE,
            mock_s3_service,
            mock_slack_service,
            mock_notify_service,
            mock_github_service,
            mock_auth0_service,
            False
        )
        mock_slack_service.send_unknown_users_slack_message.assert_not_called()
        mock_notify_service.send_first_email.assert_called_once_with(
            "some-email", "13/09/2023")
        mock_s3_service.save_emailed_users_file.assert_called_once_with(
            [{"email_address": "some-email", "username": "full-org-user", "login_date": "13/09/2023", "is_outside_collaborator": False}])
        mock_slack_service.send_undelivered_emails_slack_message.assert_not_called()


@patch("python.services.s3_service.S3Service")
@patch("python.services.notify_service.NotifyService")
class TestRunStepTwo(unittest.TestCase):
    def test_run_step_two_in_debug_mode(self, mock_notify_service, mock_s3_service):
        mock_s3_service.get_users_have_emailed.return_value = [
            create_saved_json_file_user("full-org-user"),
            create_saved_json_file_user("moj-operations-engineering-bot")
        ]
        run_step_two(
            MINISTRY_OF_JUSTICE,
            mock_s3_service,
            mock_notify_service,
            True
        )
        mock_notify_service.send_reminder_email.assert_not_called()

    def test_run_step_two_when_user_has_no_email_address(self, mock_notify_service, mock_s3_service):
        user1 = create_saved_json_file_user("full-org-user")
        user2 = create_saved_json_file_user("moj-operations-engineering-bot")
        user1['email_address'] = MISSING_EMAIL_ADDRESS
        user2['email_address'] = MISSING_EMAIL_ADDRESS
        mock_s3_service.get_users_have_emailed.return_value = [
            user1,
            user2
        ]
        run_step_two(
            MINISTRY_OF_JUSTICE,
            mock_s3_service,
            mock_notify_service,
            True
        )
        mock_notify_service.send_reminder_email.assert_not_called()

    def test_run_step_two_when_no_users(self, mock_notify_service, mock_s3_service):
        mock_s3_service.get_users_have_emailed.return_value = []
        run_step_two(
            MINISTRY_OF_JUSTICE,
            mock_s3_service,
            mock_notify_service,
            True
        )
        mock_notify_service.send_reminder_email.assert_not_called()

    @freeze_time("2023-07-13")
    def test_run_step_two_in_production_mode(self, mock_notify_service, mock_s3_service):
        mock_s3_service.get_users_have_emailed.return_value = [
            create_saved_json_file_user("full-org-user"),
            create_saved_json_file_user("moj-operations-engineering-bot")
        ]
        run_step_two(
            MINISTRY_OF_JUSTICE,
            mock_s3_service,
            mock_notify_service,
            False
        )
        mock_notify_service.send_reminder_email.assert_called_once_with(
            "some-email", "13/07/2023")


@patch("python.services.auth0_service.Auth0Service")
@patch("python.services.s3_service.S3Service")
@patch("python.services.github_service.GithubService")
@patch("python.services.notify_service.NotifyService")
@patch("python.services.slack_service.SlackService")
@patch("python.scripts.dormant_users.get_dormant_users")
class TestRunStepThree(unittest.TestCase):
    def test_run_step_three_when_no_dormant_users(self, mock_get_dormant_users, mock_slack_service, mock_notify_service, mock_github_service, mock_s3_service, mock_auth0_service):
        mock_github_service.get_org_members_login_names.return_value = [
            "full-org-user"]
        mock_get_dormant_users.return_value = []
        mock_s3_service.get_users_have_emailed.return_value = []
        run_step_three(
            MINISTRY_OF_JUSTICE,
            mock_s3_service,
            mock_slack_service,
            mock_notify_service,
            mock_github_service,
            mock_auth0_service,
            True
        )
        mock_github_service.remove_user_from_gitub.assert_not_called()
        mock_notify_service.send_removed_email.assert_not_called()
        mock_slack_service.send_remove_users_slack_message.assert_not_called()
        mock_s3_service.delete_emailed_users_file.assert_called_once()

    def test_run_step_three_when_in_debug_mode(self, mock_get_dormant_users, mock_slack_service, mock_notify_service, mock_github_service, mock_s3_service, mock_auth0_service):
        mock_github_service.get_org_members_login_names.return_value = [
            "full-org-user"]
        user1 = create_saved_json_file_user("full-org-user")
        user2 = create_saved_json_file_user("moj-operations-engineering-bot")
        user1['email_address'] = MISSING_EMAIL_ADDRESS
        user2['email_address'] = MISSING_EMAIL_ADDRESS
        mock_get_dormant_users.return_value = [user1]
        mock_s3_service.get_users_have_emailed.return_value = [
            user1,
            user2
        ]

        run_step_three(
            MINISTRY_OF_JUSTICE,
            mock_s3_service,
            mock_slack_service,
            mock_notify_service,
            mock_github_service,
            mock_auth0_service,
            True
        )

        mock_github_service.remove_user_from_gitub.assert_not_called()
        mock_notify_service.send_removed_email.assert_not_called()
        mock_slack_service.send_remove_users_slack_message.assert_not_called()
        mock_s3_service.delete_emailed_users_file.assert_called_once()

    def test_run_step_three_when_user_has_no_email_address(self, mock_get_dormant_users, mock_slack_service, mock_notify_service, mock_github_service, mock_s3_service, mock_auth0_service):
        mock_github_service.get_org_members_login_names.return_value = [
            "full-org-user"]
        mock_get_dormant_users.return_value = [
            create_saved_json_file_user("full-org-user")]
        mock_s3_service.get_users_have_emailed.return_value = [
            create_saved_json_file_user("full-org-user"),
            create_saved_json_file_user("moj-operations-engineering-bot")
        ]
        run_step_three(
            MINISTRY_OF_JUSTICE,
            mock_s3_service,
            mock_slack_service,
            mock_notify_service,
            mock_github_service,
            mock_auth0_service,
            True
        )

        mock_github_service.remove_user_from_gitub.assert_not_called()
        mock_notify_service.send_removed_email.assert_not_called()
        mock_slack_service.send_remove_users_slack_message.assert_not_called()
        mock_s3_service.delete_emailed_users_file.assert_called_once()

    def test_run_step_three_when_in_production_mode(self, mock_get_dormant_users, mock_slack_service, mock_notify_service, mock_github_service, mock_s3_service, mock_auth0_service):
        mock_github_service.get_org_members_login_names.return_value = [
            "full-org-user"]
        mock_get_dormant_users.return_value = [
            create_saved_json_file_user("full-org-user")]
        mock_s3_service.get_users_have_emailed.return_value = [
            create_saved_json_file_user("full-org-user"),
            create_saved_json_file_user("moj-operations-engineering-bot")
        ]
        run_step_three(
            MINISTRY_OF_JUSTICE,
            mock_s3_service,
            mock_slack_service,
            mock_notify_service,
            mock_github_service,
            mock_auth0_service,
            False
        )

        mock_github_service.remove_user_from_gitub.assert_called_once_with(
            "full-org-user")
        mock_notify_service.send_removed_email.assert_called_once_with(
            "some-email")
        mock_slack_service.send_remove_users_slack_message.assert_called_once_with(
            1, MINISTRY_OF_JUSTICE)
        mock_s3_service.delete_emailed_users_file.assert_called_once()


if __name__ == "__main__":
    unittest.main()
