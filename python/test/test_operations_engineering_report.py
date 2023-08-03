import unittest
from unittest import mock

from python.services.operations_engineering_reports import \
    OperationsEngineeringReportsService


class TestOperationsEngineeringReportsService(unittest.TestCase):

    @mock.patch('python.services.operations_engineering_reports.requests.Session')
    def test_override_repository_standards_reports_success(self, mock_session):
        # Mock the response object and its status_code attribute
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_session.return_value.post.return_value = mock_response

        # Create an instance of the service
        service = OperationsEngineeringReportsService(
            url='https://example.com',
            endpoint='reports',
            api_key='test_api_key'
        )

        # Prepare the data for the test
        test_data = [{'report_id': 1, 'data': 'report data 1'}, {'report_id': 2, 'data': 'report data 2'}]

        # Call the method being tested
        service.override_repository_standards_reports(test_data)

        # Assertions
        mock_session.assert_called_once()  # Ensure that the Session object is created once
        mock_session.return_value.post.assert_called_once_with(
            'https://example.com/reports',
            headers={
                "Content-Type": "application/json",
                "X-API-KEY": 'test_api_key',
                "User-Agent": "reports-service-layer",
            },
            json=test_data,
            timeout=180,
            stream=True
        )

    @mock.patch('python.services.operations_engineering_reports.requests.Session')
    def test_override_repository_standards_reports_failure(self, mock_session):
        # Mock the response object and its status_code attribute
        mock_response = mock.Mock()
        mock_response.status_code = 500
        mock_session.return_value.post.return_value = mock_response

        # Create an instance of the service
        service = OperationsEngineeringReportsService(
            url='https://example.com',
            endpoint='reports',
            api_key='test_api_key'
        )

        # Prepare the data for the test
        test_data = [{'report_id': 1, 'data': 'report data 1'}, {'report_id': 2, 'data': 'report data 2'}]

        # Call the method being tested, and expect an Exception to be raised
        with self.assertRaises(ValueError) as context:
            service.override_repository_standards_reports(test_data)

        # Assertions
        mock_session.assert_called_once()  # Ensure that the Session object is created once
        mock_session.return_value.post.assert_called_once()

if __name__ == '__main__':
    unittest.main()
