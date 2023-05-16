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


class TestRepositoryReport(unittest.TestCase):
    def setUp(self):
        self.repository_data = {
            "node": {
                "branchProtectionRules": {
                    "edges": [
                        {
                            "node": {
                                "pattern": "main",
                                "requiresApprovingReviews": True,
                                "isAdminEnforced": True,
                                "requiresCodeOwnerReviews": True,
                                "requiredApprovingReviewCount": 1,
                            }
                        }
                    ]
                },
                "defaultBranchRef": {"name": "main"},
                "description": "repo_description",
                "hasIssuesEnabled": True,
                "isArchived": False,
                "isDisabled": False,
                "isLocked": False,
                "isPrivate": False,
                "licenseInfo": None,
                "name": "repo_name",
                "pushedAt": "2022-01-01",
                "url": "https://github.com"
            }
        }

        self.repository_report = RepositoryReport(self.repository_data)

    def test_good_data_init(self):
        self.assertEqual(self.repository_report.repository_type, 'public')
        self.assertIsNot(self.repository_report.report_output, None)
        self.assertIsNot(self.repository_report.repo_data, None)
        self.assertEqual(self.repository_report.report_output['name'], self.repository_data['node']['name'])

    def test_bad_data_init(self):
        bad_data = {
            "node": {
                "hasIssuesEnabled": True,
                "licenseInfo": None,
            }
        }
        with self.assertRaises(KeyError):
            RepositoryReport(bad_data)

    def test_private_repo(self):
        self.repository_data['node']['isPrivate'] = True
        repository_report = RepositoryReport(self.repository_data)
        self.assertEqual(repository_report.repository_type, 'private')

    def test_public_repo(self):
        self.repository_data['node']['isPrivate'] = False
        repository_report = RepositoryReport(self.repository_data)
        self.assertEqual(repository_report.repository_type, 'public')

    def test_report_creation(self):
        self.assertIsNot(self.repository_report.report_output, None)
        self.assertEqual(self.repository_report.report_output['name'], self.repository_data['node']['name'])
        self.assertEqual(self.repository_report.report_output['url'], self.repository_data['node']['url'])
        self.assertEqual(self.repository_report.report_output['default_branch'], self.repository_data['node']['defaultBranchRef']['name'])
        self.assertEqual(self.repository_report.report_output['last_push'], self.repository_data['node']['pushedAt'])

    def test_report_output(self):
        self.assertIsNot(self.repository_report.report_output['report'], None)
        self.assertEqual(self.repository_report.report_output['report']['default_branch_main'], True)
        self.assertEqual(self.repository_report.report_output['report']['has_default_branch_protection'], True)
        self.assertEqual(self.repository_report.report_output['report']['has_description'], True)

    def test_compliance(self):
        self.repository_data['node']['description'] = "repo_description"
        self.repository_data['node']['licenceInfo'] = "MIT"
        bad_report = RepositoryReport(self.repository_data)
        self.assertEqual(bad_report.report_output['status'], True)

    def test_non_compliance(self):
        self.repository_data['node']['description'] = None
        bad_report = RepositoryReport(self.repository_data)
        self.assertEqual(bad_report.report_output['status'], False)
