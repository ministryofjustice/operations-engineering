import http
import unittest
import requests_mock

from python.services.operations_engineering_reports import OperationsEngineeringReportsService


class TestOrganisationStandardsReport(unittest.TestCase):

    def setUp(self):
        self.bad_mock_report = [{1}]
        self.mock_report = [{
            "default_branch": "master",
            "infractions": [
                "default_branch_main equalling False is not compliant"
            ],
            "is_private": True,
            "last_push": "2023-01-03T14:23:38Z",
            "name": "test-repo",
            "report": {
                    "administrators_require_review": False,
                    "default_branch_main": False,
                    "has_default_branch_protection": False,
                    "has_description": True,
                    "has_license": True,
                    "has_require_approvals_enabled": False,
                    "issues_section_enabled": True,
                    "requires_approving_reviews": False,
            },
            "status": False,
            "url": "https://github.com/test/test-repo"
        }]

        self.url = 'https://test.com'
        self.endpoint = 'test'
        self.api_key = 'secret'

        self.report_service = OperationsEngineeringReportsService(
            self.url, self.endpoint, self.api_key)

    def test_success_init(self):
        self.assertIsNotNone(self.report_service)

    def test_fail_init(self):
        endpoint = 'https://api.com'
        api_key = 'secret'
        with self.assertRaises(TypeError):
            OperationsEngineeringReportsService(endpoint, api_key)

    @requests_mock.Mocker()
    def test_success_override_repository_standards(self, mock):
        url = f"{self.url}/{self.endpoint}"
        mock.post(url, status_code=http.HTTPStatus.OK)
        self.report_service.override_repository_standards_reports(
            self.mock_report)

    @requests_mock.Mocker()
    def test_non200_override_repository_standards(self, m):
        url = f"{self.url}/{self.endpoint}"
        m.post(url, status_code=http.HTTPStatus.CONFLICT)
        self.assertRaises(
            Exception, self.report_service.override_repository_standards_reports, self.mock_report)

    @requests_mock.Mocker()
    def test_bad_endpoint_override_repository_standards(self, m):
        url = f"bad/{self.endpoint}"
        m.post(url, status_code=http.HTTPStatus.BAD_REQUEST)
        self.assertRaises(
            Exception, self.report_service.override_repository_standards_reports, self.mock_report)

    @requests_mock.Mocker()
    def test_bad_payload_override_repository_standards(self, m):
        url = f"{self.url}/{self.endpoint}"
        m.post(url, status_code=http.HTTPStatus.OK)
        self.assertRaises(
            TypeError, self.report_service.override_repository_standards_reports('bad_payload'))

    @requests_mock.Mocker()
    def test_bad_report_override_repository_standards(self, m):
        url = f"{self.url}/{self.endpoint}"
        m.post(url, status_code=http.HTTPStatus.OK)
        self.assertRaises(
            TypeError, self.report_service.override_repository_standards_reports, self.bad_mock_report)


if __name__ == '__main__':
    unittest.main()
