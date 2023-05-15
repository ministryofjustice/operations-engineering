import base64
import os
import unittest

import requests_mock

from python.lib.repository_standards import OrganisationStandardsReport, RepositoryReport


class TestOrganisationStandardsReport(unittest.TestCase):

    @staticmethod
    def mock_repo_data():
        return {
            "node": {
                "hasIssuesEnabled": True,
                "licenseInfo": None,
                "description": "repo_description",
                "isLocked": False,
                "isDisabled": False,
                "isArchived": False,
                "name": "repo_name",
                "defaultBranchRef": {"name": "main"},
                "url": "https://github.com",
                "pushedAt": "2022-01-01",
                "isPrivate": False,
                "branchProtectionRules": {"edges": []}
            }
        }

    def setUp(self):
        self.endpoint = 'https://test.com'
        self.api_key = 'secret'
        self.encryption_key = base64.urlsafe_b64encode(os.urandom(32))

        self.report_type = 'public'
        self.mock_report = OrganisationStandardsReport(self.endpoint, self.api_key, self.encryption_key, self.report_type)

    def testSuccessInit(self):
        self.assertEqual(self.mock_report.api_key, self.api_key)
        self.assertEqual(self.mock_report.encryption_key, self.encryption_key)
        self.assertEqual(self.mock_report.report_type, self.report_type)
        self.assertEqual(self.mock_report.report, [])

    def testFailInit(self):
        endpoint = 'https://api.com'
        api_key = 'secret'
        encryption_key = 'encryption_key'
        with self.assertRaises(ValueError):
            OrganisationStandardsReport(endpoint, api_key, encryption_key, 'invalid_type')

    def test_add(self):
        self.assertEqual(len(self.mock_report.report), 0)
        repository_report = RepositoryReport(self.mock_repo_data())

        self.mock_report.add(repository_report)
        self.assertEqual(len(self.mock_report.report), 1)

    @requests_mock.Mocker()
    def test_send_to_api_with_requests_mock(self, m):
        self.mock_report.report = [RepositoryReport(self.mock_repo_data())]
        m.post('https://test.com', json={"status": "ok"})
        self.assertIsNone(self.mock_report.send_to_api())

    @requests_mock.Mocker()
    def test_send_to_api_with_empty_report(self, m):
        self.mock_report.report = []
        m.post('https://test.com', json={"status": "ok"})
        self.assertRaises(ValueError, self.mock_report.send_to_api)

    @requests_mock.Mocker()
    def test_with_bad_status_code(self, m):
        self.mock_report.report = []
        m.post('https://test.com', json={"status": "400"})
        self.assertRaises(ValueError, self.mock_report.send_to_api)

    @requests_mock.Mocker()
    def test_fail_on_bad_request(self, m):
        self.mock_report.report = [RepositoryReport(self.mock_repo_data())]
        m.post('https://test.com', json={"status": "408"})
        self.assertIsNone(self.mock_report.send_to_api())

    def test_encrypt_string(self):
        key = self.mock_report.encrypt()
        self.assertIsInstance(key, str)
        self.assertGreater(len(key), 99)




