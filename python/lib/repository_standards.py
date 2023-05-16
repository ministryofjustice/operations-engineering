"""
This module contains the classes used to generate the repository standards report.

- The OrganisationStandardsReport class is used to generate a report for a given organisation.
- The RepositoryStandards class is used to generate a report for a given repository.

The report is generated to publish which repositories are compliant with the standards set out by the
Operations Engineering team. The report is sent to the operations-engineering-reports API.
"""
import requests
from cryptography.fernet import Fernet


class OrganisationStandardsReport:
    """
    This class is used to generate a report for a given organisation.
    The most important aspect of this class is the report collection, which should contain a list of
    RepositoryStandards objects.
    """
    def __init__(self, endpoint, api_key, enc_key, report_type: str):
        self.report = []
        self.api_endpoint = endpoint
        self.api_key = api_key
        self.encryption_key = enc_key

        # report_type can be either public or private, this is used to determine the endpoint sent to.
        self.report_type = self.__validate_report_type(report_type)

    @staticmethod
    def __validate_report_type(report_type: str) -> str:
        """
        Validate the type of report being generated. This can be either public or private and will raise an
        exception if the report type is invalid.
        """
        match report_type:
            case "public":
                return "public"
            case "private":
                return "private"
            case _:
                raise ValueError("Invalid report type")

    def add(self, report) -> None:
        """
        Add a RepositoryStandards object to the collection of reports.
        """
        self.report.append(report)

    def send_to_api(self) -> None:
        """
        Send the report to the operations-engineering-reports API. Depending on the report type, the
        endpoint will be different.
        """
        if not self.report:
            raise ValueError("Report is empty, something went wrong, we should have a report to send")

        # A decision was made to encrypt all repository data, regardless of whether it is public or private.
        data = self.__encrypt()

        status_code = self.__http_post(data)
        if status_code != 200:
            raise ValueError(f"Error sending data to site, status code: {status_code}")

    def __http_post(self, data) -> int:
        headers = {
            "Content-Type": "application/json",
            "X-API-KEY": self.api_key,
            "User-Agent": "repository-standards-report",
        }

        req = requests.post(self.api_endpoint, headers=headers,
                            json=data, timeout=3)

        return req.status_code

    def __encrypt(self):
        fernet = Fernet(self.encryption_key)

        encrypted_data_as_bytes = fernet.encrypt(bytes(str(self.report), "utf-8"))
        encrypted_data_bytes_as_string = encrypted_data_as_bytes.decode()

        return encrypted_data_bytes_as_string


class RepositoryReport:
    """
    This class is used to generate a report for a given repository. It takes a single json repository object
    from the GitHub API and returns a report of the repository. This report is used to determine if the
    repository is compliant with the standards set by Ops Engineering. It will be used to formulate a table
    of repositories that are compliant and non-compliant.
    """

    def __init__(self, raw_github_data):
        """
        Initialise the class with the raw GitHub data.
        """
        self.repo_data = raw_github_data
        self.report_output = self.__generate_report()
        self.repository_type = "private" if self.__is_private() else "public"

    def __generate_report(self) -> dict:
        """
        Generate the report for the repository, used to determine if the repository is compliant or not.
        """
        return {
            "name": self.__repo_name(),
            "default_branch": self.__default_branch(),
            "url": self.__url(),
            "status": self.is_compliant(),
            "report": self.compliance_report(),
            "last_push": self.__last_push(),
            "is_private": self.__is_private()
        }

    def __repo_name(self) -> str:
        return self.repo_data["node"]["name"]

    def __default_branch(self) -> str:
        return self.repo_data["node"]["defaultBranchRef"]["name"]

    def __url(self) -> str:
        return self.repo_data["node"]["url"]

    def is_compliant(self) -> bool:
        """
        Returns True if the repository is compliant, False otherwise.
        """
        for key, value in self.compliance_report().items():
            if value is False:
                print(f"Non-compliant: {key} is {value}")
                return False

        return True

    def __last_push(self) -> str:
        return self.repo_data["node"]["pushedAt"]

    def __is_private(self) -> bool:
        return self.repo_data["node"]["isPrivate"]

    def compliance_report(self) -> dict:
        """
        Returns a dictionary of the compliance report for the repository. The report is an opinionated
        view of what is compliant and what is not. This is based on the standards set by Ops Engineering.
        """
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
        if self.repo_data["node"]["defaultBranchRef"]["name"] == "main":
            return True
        return False

    def __has_default_branch_protection_enabled(self) -> bool:
        """
        Sets the default branch and checks if that branch has branch protection enabled. If it does, then
        return True, otherwise return False.
        """
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
