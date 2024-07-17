import os
from datetime import date, datetime
import unittest
from freezegun import freeze_time
from unittest.mock import call, patch, MagicMock
from services.slack_service import SlackService
from bin.support_stats_reporting import (
    SupportRequest,
    create_dataframe_from_csv,
    get_previous_working_day,
    get_previous_working_day,
    get_environment_variables,
    get_dict_of_requests_and_volume,
    craft_message_to_slack,
    get_support_requests_from_csv,
    get_list_of_support_requests,
    get_yesterdays_support_requests,
    main,
)


# class TestSupportRequest(unittest.TestCase):
#     @patch.dict(os.environ, {"ADMIN_SLACK_TOKEN": "token"})
#     def test_returns_variables(self):
#         slack_token = get_environment_variables()
#         self.assertEqual(slack_token, "token")
class TestGetPreviousWorkingDay(unittest.TestCase):

    def test_monday_returns_friday(self):
        previous_day = get_previous_working_day(date_today=date(2024, 7, 8))
        self.assertEqual(previous_day, str(date(2024, 7, 5)))

    def test_tuesday_returns_monday(self):
        previous_day = get_previous_working_day(date_today=date(2024, 7, 9))
        self.assertEqual(previous_day, str(date(2024, 7, 8)))


class TestGetEnvironmentVariables(unittest.TestCase):
    @patch.dict(os.environ, {"ADMIN_SLACK_TOKEN": "test_token"})
    def test_returns_variable(self):
        slack_token = get_environment_variables()
        self.assertEqual(slack_token, "test_token")

    def test_raises_error_when_no_slack_token(self):
        self.assertRaises(ValueError, get_environment_variables)


class TestCraftMessageToSlack(unittest.TestCase):
    def test_slack_message(self):

        date_today = date(2024, 7, 16)
        yesterdays_support_requests = [
            SupportRequest(
                request_type="GitHub",
                request_action="Add user to Org",
                request_date="2024-07-15",
            )
        ]
        expected_message = "On 2024-07-15 we received 1 Support Requests: \n\n--\n*Type:* GitHub\n*Action:* Add user to Org\n*Number of requests:* 1\n"
        self.assertEqual(
            craft_message_to_slack(yesterdays_support_requests, date_today),
            expected_message,
        )

    @patch.object(SlackService, "__new__")
    def test_craft_message_to_slack(self, mock_slack_service):

        mock_slack_instance = MagicMock()
        mock_slack_service.return_value = mock_slack_instance

    # @patch.object(SlackService, "send_message_to_plaintext_channel_name")

    # def test_craft_message_to_slack(self, mock_send_message_to_plaintext_channel_name):
    #     mock_send_message_to_plaintext_channel_name.assert_called_once_with(
    #         "Test message", "operations-engineering-team"
    #     )


class TestMain(unittest.TestCase):

    def test_raises_error_when_no_slack_token(self):
        self.assertRaises(ValueError, main)

    @patch("services.slack_service.SlackService.__new__")
    @patch.dict(os.environ, {"ADMIN_SLACK_TOKEN": "test_token"})
    def test_slack_message_sent_to_slack(self, mock_slack_service: MagicMock):
        # Given
        todays_date = date(2024, 7, 2)
        # When
        main(todays_date)
        # Then
        mock_slack_service.return_value.send_message_to_plaintext_channel_name.assert_called_once()
        mock_slack_service.return_value.send_message_to_plaintext_channel_name.assert_called_with(
            "On 2024-07-01 we received 0 Support Requests: \n\n",
            "operations-engineering-team",
        )
        # self.assertEqual(slack_token, "test_token")
        # slack_token = get_environment_variables()
