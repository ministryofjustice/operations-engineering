import unittest
from unittest.mock import patch

from python.services.operations_engineering_reports import \
    OperationsEngineeringReportsService


class TestOperationsEngineeringReportsService(unittest.TestCase):
    def setUp(self):
        self.service = OperationsEngineeringReportsService(
            'http://example.com', '/reports', 'api_key')
        self.reports = [
            {'repository': 'repo1', 'owner': 'owner1', 'compliant': True},
            {'repository': 'repo2', 'owner': 'owner2', 'compliant': False}
        ]

    @patch('requests.post')
    def test_override_repository_standards_reports(self, mock_post):
        mock_post.return_value.status_code = 200

        self.service.override_repository_standards_reports(self.reports)
        self.assertCountEqual(
            mock_post.call_args[1]['json'], self.reports)

    @patch('requests.post')
    def test_override_repository_standards_reports_with_non_200(self, mock_post):
        mock_post.return_value.status_code = 500

        with self.assertRaises(ValueError):
            self.service.override_repository_standards_reports(self.reports)
        mock_post.assert_called_once()


if __name__ == '__main__':
    unittest.main()
