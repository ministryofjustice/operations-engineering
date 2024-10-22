import unittest
from unittest.mock import patch
from bin.alert_on_low_gandi_funds import alert_on_low_gandi_funds


class TestAlerts(unittest.TestCase):

    def setUp(self):
        self.gandi_funds_below_threshold = 100
        self.gandi_funds_above_threshold = 600

    @patch.dict('os.environ', {'GANDI_FUNDS_TOKEN': 'test_gandi_token', 'ADMIN_SLACK_TOKEN': 'test_slack_token', 'GANDI_ORG_ID': 'test_org_id'})
    @patch('bin.alert_on_low_gandi_funds.GandiService')
    @patch('bin.alert_on_low_gandi_funds.SlackService')
    def test_alert_triggered_below_threshold(self, mock_slack_service, mock_gandi_service):
        mock_gandi_instance = mock_gandi_service.return_value
        mock_gandi_instance.get_current_account_balance_from_org.return_value = self.gandi_funds_below_threshold
        mock_slack_instance = mock_slack_service.return_value

        alert_on_low_gandi_funds()

        mock_slack_instance.send_low_gandi_funds_alert.assert_called_once()

    @patch.dict('os.environ', {'GANDI_FUNDS_TOKEN': 'test_gandi_token', 'ADMIN_SLACK_TOKEN': 'test_slack_token', 'GANDI_ORG_ID': 'test_org_id'})
    @patch('bin.alert_on_low_gandi_funds.GandiService')
    @patch('bin.alert_on_low_gandi_funds.SlackService')
    def test_no_alert_triggered_above_threshold(self, mock_slack_service, mock_gandi_service):
        mock_gandi_instance = mock_gandi_service.return_value
        mock_gandi_instance.get_current_account_balance_from_org.return_value = self.gandi_funds_above_threshold
        mock_slack_instance = mock_slack_service.return_value

        alert_on_low_gandi_funds()

        mock_slack_instance.send_low_gandi_funds_alert.assert_not_called()

    @patch.dict('os.environ', {})
    def test_exit_no_gandi_funds_token(self):
        with self.assertRaises(SystemExit):
            alert_on_low_gandi_funds()


if __name__ == '__main__':
    unittest.main()
