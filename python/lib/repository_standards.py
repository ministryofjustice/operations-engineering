"""
This file contains the classes that are used to represent the data
that will be sent to the Operations Engineering Reports API.
"""
import os
class RepositoryStandards:
    """
    This class represents the object that will be sent to the Operations Engineering Reports API.
    """
    def __init__(self, api_endpoint, encryption_key, api_secret_key, repo_data):
        self.api_endpoint = self.where_to_send(api_endpoint)
        self.encryption_key = self.enc_key(encryption_key)
        self.api_secret_key = self.api_access_key(api_secret_key)
        self.data = repo_data
        self.encrypted_data = self.send_encrypted_data()
        # TODO: Should I store the standards report in this class
        # self.standards = self.RepositoryStandards(self.data)

    def send_encrypted_data(self):
        """
        Sends the encrypted data to the API.
        """
        return ""

    def send_data(self):
        """
        Sends the data to the API.
        """
        return ""

    def enc_key(self, encryption_key):
        """
        Returns the encryption key.
        """
        if encryption_key is None:
            encryption_key = os.environ.get("ENCRYPTION_KEY")

        error = ValueError("Encryption key is not set")
        if encryption_key is None:
            raise error

        return encryption_key

    def api_access_key(self, api_secret_key):
        """
        Returns a secret key
        """
        return ""

    def where_to_send(self, api_endpoint):
        """
        Returns the API endpoint to send the data to.
        """
        # check environment variable
        return self.api_endpoint

    class StandardsReport:
        """
        Report of repositories that are maintained in the MinistryOfJustice GitHub organization.
        """

        def __init__(self, repo_data):
            """
            Single repository data as Hash/JSON
            """
            self.repo_data = repo_data
            self.status = self.status()

        def structure(self):
            """
            Returns a Hash of the repository data.
            """
            return {
                "name": self.repo_data["name"],
                "default_branch": self.repo_data["default_branch"],
                "url": self.repo_data["html_url"],
                "status": self.is_compliant(),
                "last_push": self.repo_data["pushed_at"],
                "report": self.report(),
                "is_private": self.repo_data["private"],
            }

        def is_compliant(self) -> bool:
            """
            Returns the status of the repository.
            """
            return False

        def report(self):
            """
            Returns the status of the repository report.
            """
            return {
                "default_branch_main": self.default_branch_main(),
                "has_default_branch_protection": self.has_default_branch_protection_enabled(),
                "requires_approving_reviews": self.has_requires_approving_reviews_enabled(),
                "administrators_require_review": self.has_admin_requires_reviews_enabled(),
                "issues_section_enabled": self.has_issues_enabled(),
                "has_require_approvals_enabled": self.has_required_appproval_review_count_enabled(),
                "has_license": self.has_license(),
                "has_description": self.has_description()
            }

        def default_branch_main(self) -> bool:
            """
            Returns True if the default branch is main, False otherwise.
            """
            if self.repo_data.default_branch == "main":
                return True
            return False

        def has_default_branch_protection_enabled(self) -> bool:
            """
            Returns True if the default branch is protected, False otherwise.
            """
            if self.repo_data["default_branch_protection"] is True:
                return True
            return False

        def has_requires_approving_reviews_enabled(self) -> bool:
            """
            Returns True if the repository requires approving reviews, False otherwise.
            """
            if self.repo_data["requires_approving_reviews"] is True:
                return True
            return False

        def has_admin_requires_reviews_enabled(self) -> bool:
            """
            Returns True if the repository requires admin reviews, False otherwise.
            """
            if self.repo_data["admin_requires_reviews"] is True:
                return True
            return False

        def has_issues_enabled(self) -> bool:
            """
            Returns True if the repository has issues enabled, False otherwise.
            """
            if self.repo_data["has_issues"] is True:
                return True
            return False

        def has_required_appproval_review_count_enabled(self) -> bool:
            """
            Returns True if the repository has required approving review count enabled,
            False otherwise.
            """
            if self.repo_data["required_approving_review_count"] is True:
                return True
            return False


        def has_license(self) -> bool:
            """
            Returns True if the repository has a license, False otherwise.
            """
            if self.repo_data["license"] is not None:
                return True
            return False

        def has_description(self) -> bool:
            """
            Returns True if the repository has a description, False otherwise.
            """
            if self.repo_data["description"] is not None:
                return True
            return False
