import os
import unittest
from unittest.mock import MagicMock, patch

from python.scripts import add_users_all_org_members_github_team


@patch("github.Github.__new__", new=MagicMock)
@patch("gql.Client.__new__", new=MagicMock)
@patch("gql.transport.aiohttp.AIOHTTPTransport.__new__", new=MagicMock)
class TestAddUsersEveryoneGithubTeamMain(unittest.TestCase):

    @patch.dict(os.environ, {"ADMIN_GITHUB_TOKEN": "token", "GITHUB_ORGANIZATION_NAME": "ministryofjustice"})
    def test_main_smoke_test(self):
        add_users_all_org_members_github_team.main()


class TestAddUsersEveryoneGithubTeamGetEnvironmentVariables(unittest.TestCase):
    def test_raises_error_when_no_environment_variables_provided(self):
        self.assertRaises(
            ValueError, add_users_all_org_members_github_team.get_environment_variables)

    @patch.dict(os.environ, {"GITHUB_ORGANIZATION_NAME": "ministryofjustice"})
    def test_raises_error_when_no_github_token(self):
        self.assertRaises(
            ValueError, add_users_all_org_members_github_team.get_environment_variables)

    @patch.dict(os.environ, {"ADMIN_GITHUB_TOKEN": "token"})
    def test_raises_error_when_no_github_organization(self):
        self.assertRaises(
            ValueError, add_users_all_org_members_github_team.get_environment_variables)

    @patch.dict(os.environ, {"ADMIN_GITHUB_TOKEN": "token", "GITHUB_ORGANIZATION_NAME": "ministryofjustice"})
    def test_returns_values(self):
        github_token, github_organization_name = add_users_all_org_members_github_team.get_environment_variables()
        self.assertEqual(github_token, "token")
        self.assertEqual(github_organization_name, "ministryofjustice")


class TestAddUsersEveryoneGithubTeamGetConfigForOrganization(unittest.TestCase):
    def test_raises_error_when_unknown_github_organization(self):
        self.assertRaises(
            ValueError, add_users_all_org_members_github_team.get_config_for_organization, "unknown organization"
        )

    def test_returns_values_ministryofjustice_config(self):
        organization_name, organization_team_name = add_users_all_org_members_github_team.get_config_for_organization(
            "ministryofjustice")
        self.assertEqual(organization_name, "ministryofjustice")
        self.assertEqual(organization_team_name, "all-org-members")

    def test_returns_values_moj_analytical_services_config(self):
        organization_name, organization_team_name = add_users_all_org_members_github_team.get_config_for_organization(
            "moj-analytical-services")
        self.assertEqual(organization_name, "moj-analytical-services")
        self.assertEqual(organization_team_name, "everyone")


if __name__ == "__main__":
    unittest.main()
