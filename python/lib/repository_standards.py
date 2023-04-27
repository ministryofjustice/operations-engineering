"""
This file contains the classes that are used to represent the data
that will be sent to the Operations Engineering Reports API.
"""
import json

class RepositoryReport:
    """
    Class to hold the report standards for a single repository. This standard is defined
    by the Operations Engineering team.
    """

    def __init__(self, repo_data):
        """
        Single repository data as Hash/JSON
        """
        self.repo_data = repo_data
        self.report = self.report()
        self.status = self.status()

    def structure(self):
        """
        Returns a Hash of the repository data.
        """
        return {
            "name": self.repo_data["name"],
            "default_branch": self.repo_data["default_branch"],
            "url": self.repo_data["html_url"],
            "status": self.status,
            "last_push": self.repo_data["pushed_at"],
            "report": self.report,
            "is_private": self.repo_data["private"],
        }

    def report_status(self):
        """
        Returns the status of the repository report.
        """
        return {
            "default_branch_main": self.default_branch_main(),
            "has_default_branch_protection": self.has_default_branch_protection_enabled(),
            "requires_approving_reviews": has_requires_approving_reviews_enabled(),
            "administrators_require_review": has_admin_requires_reviews_enabled(),
            "issues_section_enabled": has_issues_enabled(),
            "has_require_approvals_enabled": has_required_appproving_review_count_enabled(),
            "has_license": has_license(),
            "has_description": has_description()
        }


    def default_branch_main(self) -> bool:
        """
        Returns True if the default branch is main, False otherwise.
        """
        if self.repo_data.default_branch == "main":
            return True
        return False


class GitHubReport:
    """
    This class represents all the GitHub repositories managed by an organization.
    """
    def __init__(self, github_data):
        # Take a block of json and create a Repository report for each repository
        self.repositories = []
        for repo_data in github_data:
            self.repositories.append(RepositoryReport(repo_data))

class OperationsReport:
    """
    This class represents the object that will be sent to the Operations Engineering Reports API.
    """
    def __init__(self, report: GitHubReport):
        self.repos = report
        self.public_repos = []
        self.private_repos = []

    def public_repo_report(self):
        """
        Returns a public repository report.

        :return: OperationsReport
        """
        self.public_repos = [
            repo for repo in self.repos.repositories if repo.repo_data.is_private is False

        ]

    def private_repo_report(self):
        """
        Returns a private repository report.

        :return: OperationsReport
        """
        self.private_repos = [
            repo for repo in self.repos.repositories if repo.repo_data["private"] is True
        ]


    def to_json(self):
        """
        Converts the object to a JSON string.

        :return: JSON string
        """
        return json.dumps(self.to_hash())

    def to_hash(self):
        """
        Converts the object to a Hash.

        :return: Hash
        """
        return {
            "repository_report": self.repository_report.structure(),
        }

