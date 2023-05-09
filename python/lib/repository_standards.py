"""
This file contains the classes that are used to represent the data
that will be sent to the Operations Engineering Reports API.
"""


class RepositoryStandards:
    """
    Report of repositories that are maintained in the MinistryOfJustice GitHub organization.
    """

    def __init__(self, raw_github_data):
        """
        Single repository data as Hash/JSON
        """
        self.repo_data = raw_github_data
        self.report_output = self.report()

    def report(self):
        """
        Returns a Hash of the repository data.
        """
        return {
            "name": self.repo_name(),
            "default_branch": self.default_branch(),
            "url": self.url(),
            "status": self.is_compliant(),
            "last_push": self.last_push(),
            "is_private": self.is_private()
        }

    def repo_name(self) -> str:
        """
        Returns the name of the repository.
        """
        return self.repo_data["node"]["name"]

    def default_branch(self) -> str:
        """
        Returns the default branch of the repository.
        """
        return self.repo_data["node"]["defaultBranchRef"]["name"]

    def url(self) -> str:
        """
        Returns the URL of the repository.
        """
        return self.repo_data["node"]["url"]

    def is_compliant(self) -> bool:
        """
        Returns True if the repository is compliant, False otherwise.
        """
        for key, value in self.compliance_report().items():
            if value is False:
                return False

        return True

    def last_push(self) -> str:
        """
        Returns the last push date of the repository.
        """
        return self.repo_data["node"]["pushedAt"]

    def is_private(self) -> bool:
        """
        Returns True if the repository is private, False otherwise.
        """
        return self.repo_data["node"]["isPrivate"]

    def compliance_report(self) -> dict:
        """
        Returns the status of the repository.
        """
        return {
            "default_branch_main": self.default_branch_main(),
            "has_default_branch_protection": self.has_default_branch_protection_enabled(),
            "requires_approving_reviews": self.has_requires_approving_reviews_enabled(),
            "administrators_require_review": self.has_admin_requires_reviews_enabled(),
            "issues_section_enabled": self.has_issues_enabled(),
            "has_require_approvals_enabled": self.has_required_approval_review_count_enabled(),
            "has_license": self.has_license(),
            "has_description": self.has_description()
        }

    def default_branch_main(self) -> bool:
        """
        Returns True if the default branch is main, False otherwise.
        """
        if self.repo_data["node"]["defaultBranchRef"]["name"] == "main":
            return True
        return False

    def has_default_branch_protection_enabled(self) -> bool:
        """
        Returns True if the default branch is protected, False otherwise.
        """
        default_branch = self.repo_data["node"]["defaultBranchRef"]["name"]
        branch_protection_rules = self.repo_data["node"]["branchProtectionRules"]["edges"]
        for branch_protection_rule in branch_protection_rules:
            branch_protection_rules = branch_protection_rule["node"]["pattern"]
            if branch_protection_rules == default_branch:
                return True
            return False

    def has_requires_approving_reviews_enabled(self) -> bool:
        """
        Returns True if the repository requires approving reviews, False otherwise.
        """
        branch_protection_rules = self.repo_data["node"]["branchProtectionRules"]["edges"]
        for branch_protection_rule in branch_protection_rules:
            return branch_protection_rule["node"]["requiresApprovingReviews"]

    def has_admin_requires_reviews_enabled(self) -> bool:
        """
        Returns True if the repository requires admin reviews, False otherwise.
        """
        branch_protection_rules = self.repo_data["node"]["branchProtectionRules"]["edges"]
        for branch_protection_rule in branch_protection_rules:
            return branch_protection_rule["node"]["isAdminEnforced"]

    def has_issues_enabled(self) -> bool:
        """
        Returns True if the repository has issues enabled, False otherwise.
        """
        return self.repo_data["node"]["hasIssuesEnabled"]

    def has_required_approval_review_count_enabled(self) -> bool:
        """
        Returns True if the repository has required approving review count enabled,
        False otherwise.
        """
        branch_protection_rules = self.repo_data["node"]["branchProtectionRules"]["edges"]
        for branch_protection_rule in branch_protection_rules:
            if branch_protection_rule["node"]["requiredApprovingReviewCount"] > 0:
                return True
            return False

    def has_license(self) -> bool:
        """
        Returns True if the repository has a license, False otherwise.
        """
        if self.repo_data["node"]["licenseInfo"] is not None:
            return True
        return False

    def has_description(self) -> bool:
        """
        Returns True if the repository has a description, False otherwise.
        """
        if self.repo_data["node"]["description"] is not None:
            return True
        return False
