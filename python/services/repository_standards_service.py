"""
This module contains the classes used to generate the GitHub repository standards report.

- The OrganisationStandardsReport class is used to generate a report for a given organisation.
- The RepositoryStandards class is used to generate a report for a given repository.

The report is generated to publish which repositories are compliant with the standards set out by the
Operations Engineering team. The report is sent to the operations-engineering-reports API.
"""
import json
from dataclasses import dataclass


@dataclass
class GitHubRepositoryStandardsReport:
    name: str
    status: bool
    last_push: str
    is_private: bool
    default_branch: str
    url: str
    report: dict
    infractions: list

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)


class RepositoryReport:
    """
    This class is used to generate a report for a given repository. It takes a single json repository object
    from the GitHub API and returns a report of the repository. This report is used to determine if the
    repository is compliant with the standards set by Ops Engineering. It will be used to formulate a table
    of repositories that are compliant and non-compliant.
    """

    def __init__(self, raw_github_data) -> None:
        # A list of reasons why the repository is non-compliant
        self.infractions = []
        self.repo_data = raw_github_data
        self.report_output = self.__generate_report()
        self.is_compliant = self.__is_compliant()
        self.repository_type = "private" if self.__is_private() else "public"

    def __generate_report(self) -> GitHubRepositoryStandardsReport:
        return GitHubRepositoryStandardsReport(
            name=self.__repo_name(),
            status=self.__is_compliant(),
            last_push=self.__last_push(),
            is_private=self.__is_private(),
            default_branch=self.__default_branch(),
            url=self.__url(),
            report=self.__compliance_report(),
            infractions=self.infractions
        )

    def __repo_name(self) -> str:
        return self.repo_data["node"]["name"]

    def __default_branch(self) -> str:
        return self.repo_data["node"]["defaultBranchRef"]["name"]

    def __url(self) -> str:
        return self.repo_data["node"]["url"]

    def __is_compliant(self) -> bool:
        for key, value in self.__compliance_report().items():
            if value is False:
                self.infractions.append("Non-compliant: {key} is {value}")
                return False

        return True

    def __last_push(self) -> str:
        return self.repo_data["node"]["pushedAt"]

    def __is_private(self) -> bool:
        return self.repo_data["node"]["isPrivate"]

    def __compliance_report(self) -> dict:
        return {
            "default_branch_main": self.__default_branch_main(),
            "has_default_branch_protection": self.__has_default_branch_protection_enabled(),
            "requires_approving_reviews": self.__has_requires_approving_reviews_enabled(),
            "administrators_require_review": self.__has_admin_requires_reviews_enabled(),
            "issues_section_enabled": self.__has_issues_enabled(),
            "has_require_approvals_enabled": self.__has_required_approval_review_count_enabled(),
            "has_license": self.__has_license(),
            "has_description": self.__has_description()
        }

    def __default_branch_main(self) -> bool:
        return self.repo_data["node"]["defaultBranchRef"]["name"] == "main"

    def __has_default_branch_protection_enabled(self) -> bool:
        default_branch = self.repo_data["node"]["defaultBranchRef"]["name"]
        branch_protection_rules = self.repo_data["node"]["branchProtectionRules"]["edges"]
        for branch_protection_rule in branch_protection_rules:
            branch_protection_rules = branch_protection_rule["node"]["pattern"]
            if branch_protection_rules == default_branch:
                return True
            return False

    def __has_requires_approving_reviews_enabled(self) -> bool:
        branch_protection_rules = self.repo_data["node"]["branchProtectionRules"]["edges"]
        for branch_protection_rule in branch_protection_rules:
            return branch_protection_rule["node"]["requiresApprovingReviews"]

    def __has_admin_requires_reviews_enabled(self) -> bool:
        branch_protection_rules = self.repo_data["node"]["branchProtectionRules"]["edges"]
        for branch_protection_rule in branch_protection_rules:
            return branch_protection_rule["node"]["isAdminEnforced"]

    def __has_issues_enabled(self) -> bool:
        return self.repo_data["node"]["hasIssuesEnabled"]

    def __has_required_approval_review_count_enabled(self) -> bool:
        branch_protection_rules = self.repo_data["node"]["branchProtectionRules"]["edges"]
        for branch_protection_rule in branch_protection_rules:
            if branch_protection_rule["node"]["requiredApprovingReviewCount"] > 0:
                return True
            return False

    def __has_license(self) -> bool:
        if not self.repo_data["node"]["licenseInfo"]:
            return True
        return False

    def __has_description(self) -> bool:
        if self.repo_data["node"]["description"] is not None:
            return True
        return False
