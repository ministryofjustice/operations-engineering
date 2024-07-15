import os
from datetime import date, datetime
import unittest
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

    def test_monday_returns_friday(self, mock_date: MagicMock):
        mock_date.return_value.today.return_value = date("2024-07-08")
        previous_day = get_previous_working_day()
        self.assertEqual(previous_day, date("2024-07-05"))


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
        previous_support_day = "2024-07-11"
        yesterdays_support_requests = 8
        expected_message = "On 2024-07-11 we recieved 8 Support Requests: \n\n--\n*Type:* GitHub\n*Action:* Add user to Org\n*Number of Requests:* 8"
        self.assertEqual(
            craft_message_to_slack(previous_support_day),
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
