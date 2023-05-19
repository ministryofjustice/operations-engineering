import json
import unittest

from python.services.standards_service import RepositoryReport


class TestCompliantRepositoryReport(unittest.TestCase):
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
                "licenseInfo": "MIT",
                "name": "repo_name",
                "pushedAt": "2022-01-01",
                "url": "https://github.com"
            }
        }

        self.repository_report = RepositoryReport(self.repository_data)
        self.to_json = json.loads(self.repository_report.output)

    def test_good_data_init(self):
        self.assertIsNot(self.repository_report, None)

    def test_bad_data_init(self):
        bad_data = {
            "node": {
                "hasIssuesEnabled": True,
                "licenseInfo": None,
            }
        }
        with self.assertRaises(KeyError):
            RepositoryReport(bad_data)

    def test_report_creation(self):
        self.assertIsNot(self.repository_report.output, None)

    def test_report_output(self):
        self.assertEqual(self.to_json['status'], True)

    def test_report_output_keys(self):
        self.assertEqual(len(self.to_json.keys()), 8)

    def test_compliance_report(self):
        self.assertEqual(self.to_json['report']['administrators_require_review'], True)
        self.assertEqual(self.to_json['report']['default_branch_main'], True)
        self.assertEqual(self.to_json['report']['has_default_branch_protection'], True)
        self.assertEqual(self.to_json['report']['has_license'], True)


class TestNonCompliantRepositoryReport(unittest.TestCase):
    def setUp(self):
        self.repository_data = {
            "node": {
                "branchProtectionRules": {
                    "edges": [
                        {
                            "node": {
                                "pattern": "not_main",
                                "requiresApprovingReviews": False,
                                "isAdminEnforced": False,
                                "requiresCodeOwnerReviews": True,
                                "requiredApprovingReviewCount": 1,
                            }
                        }
                    ]
                },
                "defaultBranchRef": {"name": "main"},
                "description": "repo_description",
                "hasIssuesEnabled": False,
                "isArchived": False,
                "isDisabled": False,
                "isLocked": False,
                "isPrivate": True,
                "licenseInfo": None,
                "name": "repo_name",
                "pushedAt": "2022-01-01",
                "url": "https://github.com"
            }
        }

        self.repository_report = RepositoryReport(self.repository_data)
        self.to_json = json.loads(self.repository_report.output)

    def test_bad_data_report_output(self):
        self.assertEqual(self.to_json['status'], False)

    def test_bad_data_report_output_keys(self):
        self.assertEqual(len(self.to_json.keys()), 8)

    def test_bad_data_compliance_report(self):
        self.assertEqual(self.to_json['report']['administrators_require_review'], False)
        self.assertEqual(self.to_json['report']['has_default_branch_protection'], False)
        self.assertEqual(self.to_json['report']['has_license'], False)


if __name__ == '__main__':
    unittest.main()