import json
import unittest

from services.standards_service import RepositoryReport


class TestCompliantRepositoryReport(unittest.TestCase):
    def setUp(self):
        self.repository_data = {
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
            "url": "https://github.com",
            "repositoryTopics": {
                "edges": [
                    {'node': {'topic': {'name': 'topic-1'}}},
                    {'node': {'topic': {'name': 'topic-2'}}}
                ]
            }
        }

        self.repository_report = RepositoryReport(self.repository_data)
        self.to_json = json.loads(self.repository_report.output)

    def test_good_data_init(self):
        self.assertIsNot(self.repository_report, None)

    def test_bad_data_init(self):
        bad_data = {
            "hasIssuesEnabled": True,
            "licenseInfo": None,
        }
        with self.assertRaises(KeyError):
            RepositoryReport(bad_data)

    def test_report_creation(self):
        self.assertIsNot(self.repository_report.output, None)

    def test_report_output(self):
        self.assertEqual(self.to_json['status'], True)

    def test_report_output_keys(self):
        self.assertEqual(len(self.to_json.keys()), 9)

    def test_compliance_report(self):
        self.assertEqual(self.to_json['report']
                         ['administrators_require_review'], True)
        self.assertEqual(self.to_json['report']['default_branch_main'], True)
        self.assertEqual(self.to_json['report']
                         ['has_default_branch_protection'], True)
        self.assertEqual(self.to_json['report']['has_license'], True)


class TestNonCompliantRepositoryReport(unittest.TestCase):
    def setUp(self):
        self.repository_data = {
            "branchProtectionRules": {
                "edges": [
                    {
                        "node": {
                            "pattern": "not_main",
                            "requiresApprovingReviews": False,
                            "isAdminEnforced": False,
                            "requiresCodeOwnerReviews": True,
                            "requiredApprovingReviewCount": 0,
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
            "url": "https://github.com",
            "repositoryTopics": { # Non-empty topic raw format
                "edges": [
                    {'node': {'topic': {'name': 'topic-1'}}},
                    {'node': {'topic': {'name': 'topic-2'}}}
                ]
            }            
        }

        self.repository_report = RepositoryReport(self.repository_data)
        self.to_json = json.loads(self.repository_report.output)

    def test_bad_data_report_output(self):
        self.assertEqual(self.to_json['status'], False)

    def test_bad_data_report_output_keys(self):
        self.assertEqual(len(self.to_json.keys()), 9)

    def test_bad_data_compliance_report(self):
        self.assertEqual(self.to_json['report']
                         ['administrators_require_review'], False)
        self.assertEqual(self.to_json['report']
                         ['has_default_branch_protection'], False)
        self.assertEqual(self.to_json['report']['has_license'], False)
        self.assertEqual(self.to_json['report']
                         ['has_require_approvals_enabled'], False)
        self.assertEqual(self.to_json['report']
                         ['administrators_require_review'], False)
        self.assertEqual(self.to_json['report']
                         ['requires_approving_reviews'], False)

    def test_empty_admin_approvals(self):
        self.repository_data['branchProtectionRules']['edges'][0]['node']['requiredApprovingReviewCount'] = None
        self.repository_report = RepositoryReport(self.repository_data)
        self.to_json = json.loads(self.repository_report.output)
        self.assertEqual(self.to_json['report']
                         ['has_require_approvals_enabled'], False)

    def test_empty_require_approvers(self):
        self.repository_data['branchProtectionRules']['edges'][0]['node']['requiresApprovingReviews'] = None
        self.repository_report = RepositoryReport(self.repository_data)
        self.to_json = json.loads(self.repository_report.output)
        self.assertEqual(self.to_json['report']
                         ['has_require_approvals_enabled'], False)

    def test_empty_admin_requires_reviews_enabled(self):
        self.repository_data['branchProtectionRules']['edges'][0]['node']['isAdminEnforced'] = None
        self.repository_report = RepositoryReport(self.repository_data)
        self.to_json = json.loads(self.repository_report.output)
        self.assertEqual(self.to_json['report']
                         ['has_default_branch_protection'], False)

    def test_empty_description(self):
        self.repository_data['description'] = None
        self.repository_report = RepositoryReport(self.repository_data)
        self.to_json = json.loads(self.repository_report.output)
        self.assertEqual(self.to_json['report']['has_description'], False)

    def test_empty_branch_protection_settings(self):
        self.repository_data['branchProtectionRules']["edges"] = None
        self.repository_report = RepositoryReport(self.repository_data)
        self.to_json = json.loads(self.repository_report.output)
        self.assertEqual(self.to_json['report']
                         ['has_default_branch_protection'], False)

    def test_empty_branch_condition(self):
        empty_data_set = {
            "branchProtectionRules": {
                "edges": [
                    {
                        "node": {
                            "pattern": "not_main",
                            "requiresApprovingReviews": False,
                            "isAdminEnforced": False,
                            "requiresCodeOwnerReviews": True,
                            "requiredApprovingReviewCount": 0,
                        }
                    }
                ]
            },
            "defaultBranchRef": None,
            "description": "repo_description",
            "hasIssuesEnabled": False,
            "isArchived": False,
            "isDisabled": False,
            "isLocked": False,
            "isPrivate": True,
            "licenseInfo": None,
            "name": "repo_name",
            "pushedAt": "2022-01-01",
            "url": "https://github.com",
            "repositoryTopics": {"edges": []} # Empty topic raw format
        }
        repository_report = RepositoryReport(empty_data_set)
        to_json = json.loads(repository_report.output)
        self.assertEqual(to_json['report']['default_branch_main'], False)


if __name__ == '__main__':
    unittest.main()
