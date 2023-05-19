"""
This module contains the classes used to generate the GitHub repository standards report.

The report is generated to publish which repositories are compliant with the standards set out by
the Operations Engineering team.
"""
import json
from dataclasses import dataclass


@dataclass
class GitHubRepositoryStandardsReport:
    """A dataclass used to generate a report for a given repository."""
    default_branch: str
    infractions: list
    is_private: bool
    last_push: str
    name: str
    report: dict
    status: bool
    url: str

    def to_json(self) -> str:
        """Convert the dataclass to a json object."""
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)


class RepositoryReport:
    """A class used to generate a report for a given repository. The report will represent standards
    set out by the Operations Engineering team. If a repository is non-compliant, the report will
    contain a list of reasons why the repository is non-compliant.

    Arguments:
        raw_github_data {dict} -- The raw data returned from the GitHub API for a given repository.

    """

    def __init__(self, raw_github_data) -> None:
        # A list of reasons why the repository is non-compliant
        self.__infractions = []
        self.__github_data = raw_github_data
        self.output = self.__generate_report()

    def __generate_report(self) -> str:
        return GitHubRepositoryStandardsReport(
            name=self.__repo_name(),
            status=self.__check_compliant(),
            last_push=self.__last_push(),
            is_private=self.__is_private(),
            default_branch=self.__default_branch(),
            url=self.__url(),
            report=self.__compliance_report(),
            infractions=self.__infractions
        ).to_json()

    def __repo_name(self) -> str:
        return self.__github_data["node"]["name"]

    def __default_branch(self) -> str:
        return self.__github_data["node"]["defaultBranchRef"]["name"]

    def __url(self) -> str:
        return self.__github_data["node"]["url"]

    def __check_compliant(self) -> bool:
        for key, value in self.__compliance_report().items():
            if value is False:
                self.__infractions.append(f"{key} equalling {value} is not compliant")
                return False

        return True

    def __last_push(self) -> str:
        return self.__github_data["node"]["pushedAt"]

    def __is_private(self) -> bool:
        return self.__github_data["node"]["isPrivate"]

    def __compliance_report(self) -> dict:
        return {
            "administrators_require_review": self.__has_admin_requires_reviews_enabled(),
            "default_branch_main": self.__default_branch_main(),
            "has_default_branch_protection": self.__has_default_branch_protection_enabled(),
            "has_description": self.__has_description(),
            "has_license": self.__has_license(),
            "has_require_approvals_enabled": self.__has_required_approval_review_count_enabled(),
            "issues_section_enabled": self.__has_issues_enabled(),
            "requires_approving_reviews": self.__has_requires_approving_reviews_enabled(),
        }

    def __default_branch_main(self) -> bool:
        return self.__github_data["node"]["defaultBranchRef"]["name"] == "main"

    def __has_default_branch_protection_enabled(self) -> bool:
        default_branch = self.__github_data["node"]["defaultBranchRef"]["name"]
        branch_protection_rules = self.__github_data["node"]["branchProtectionRules"]["edges"]
        for branch_protection_rule in branch_protection_rules:
            branch_rule = branch_protection_rule["node"]["pattern"]
            if branch_rule == default_branch:
                return True
            return False

    def __has_requires_approving_reviews_enabled(self) -> bool:
        branch_protection_rules = self.__github_data["node"]["branchProtectionRules"]["edges"]
        for branch_protection_rule in branch_protection_rules:
            if branch_protection_rule["node"]["requiresApprovingReviews"] is None:
                return False
            return branch_protection_rule["node"]["requiresApprovingReviews"]

    def __has_admin_requires_reviews_enabled(self) -> bool:
        branch_protection_rules = self.__github_data["node"]["branchProtectionRules"]["edges"]
        for branch_protection_rule in branch_protection_rules:
            if branch_protection_rule["node"]["isAdminEnforced"] is None:
                return False
            return branch_protection_rule["node"]["isAdminEnforced"]

    def __has_issues_enabled(self) -> bool:
        return self.__github_data["node"]["hasIssuesEnabled"]

    def __has_required_approval_review_count_enabled(self) -> bool:
        branch_protection_rules = self.__github_data["node"]["branchProtectionRules"]["edges"]
        for branch_protection_rule in branch_protection_rules:
            if branch_protection_rule["node"]["requiredApprovingReviewCount"] is None:
                return False
            if branch_protection_rule["node"]["requiredApprovingReviewCount"] > 0:
                return True
            return False

    def __has_license(self) -> bool:
        if self.__github_data["node"]["licenseInfo"] is not None:
            return True
        return False

    def __has_description(self) -> bool:
        if self.__github_data["node"]["description"] is not None:
            return True
        return False
