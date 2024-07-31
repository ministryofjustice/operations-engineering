import os
from datetime import date
import unittest
from unittest.mock import patch, MagicMock
from services.slack_service import SlackService
from bin.support_stats_reporting import (
    SupportRequest,
    get_previous_working_day,
    get_environment_variables,
    craft_message_to_slack,
    main,
)


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


class TestMain(unittest.TestCase):

    def test_raises_error_when_no_slack_token(self):
        self.assertRaises(ValueError, main)

    @patch("services.slack_service.SlackService.__new__")
    @patch.dict(os.environ, {"ADMIN_SLACK_TOKEN": "test_token"})
    def test_slack_message_sent_to_slack(self, mock_slack_service: MagicMock):

        todays_date = date(2024, 7, 23)
        file_path = "test/fixtures/test_data.csv"

        main(todays_date, file_path)

        mock_slack_service.return_value.send_message_to_plaintext_channel_name.assert_called_once()
        mock_slack_service.return_value.send_message_to_plaintext_channel_name.assert_called_with(
            "On 2024-07-22 we received 8 Support Requests: \n\n--\n*Type:* GitHub\n*Action:* GitHub – add user to org\n*Number of requests:* 2\n--\n*Type:* GitHub\n*Action:* GitHub – remove user from org\n*Number of requests:* 1\n--\n*Type:* 1Password\n*Action:* 1Password - information/help\n*Number of requests:* 1\n--\n*Type:* API\n*Action:* API Key\n*Number of requests:* 1\n--\n*Type:* DNS\n*Action:* DNS/Domain\n*Number of requests:* 1\n--\n*Type:* Other\n*Action:* Tools Information/help\n*Number of requests:* 1\n--\n*Type:* Other\n*Action:* Refer to another team\n*Number of requests:* 1\n",
            "operations-engineering-team",
        )

    @patch("services.slack_service.SlackService.__new__")
    @patch.dict(os.environ, {"ADMIN_SLACK_TOKEN": "test_token"})
    def test_slack_message_sent_to_slack_with_no_request_data(
        self, mock_slack_service: MagicMock
    ):

        todays_date = date(2024, 7, 24)
        file_path = "test/fixtures/test_data.csv"

        main(todays_date, file_path)

        mock_slack_service.return_value.send_message_to_plaintext_channel_name.assert_called_once()
        mock_slack_service.return_value.send_message_to_plaintext_channel_name.assert_called_with(
            "On 2024-07-23 we received 0 Support Requests: \n\n",
            "operations-engineering-team",
        )
