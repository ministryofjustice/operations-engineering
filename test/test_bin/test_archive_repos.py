# pylint: disable=C0411

import os
import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch

from dateutil.relativedelta import relativedelta
from freezegun import freeze_time

from bin import archive_repositories


@patch("github.Github.__new__", new=MagicMock)
@patch("gql.Client.__new__", new=MagicMock)
@patch("gql.transport.aiohttp.AIOHTTPTransport.__new__", new=MagicMock)
class TestAddUsersEveryoneGithubTeamMain(unittest.TestCase):

    @patch.dict(os.environ, {"ADMIN_GITHUB_TOKEN": "token", "GITHUB_ORGANIZATION_NAME": "ministryofjustice"})
    def test_main_smoke_test(self):
        archive_repositories.main()


class TestAddUsersEveryoneGithubTeamGetEnvironmentVariables(unittest.TestCase):
    def test_raises_error_when_no_environment_variables_provided(self):
        self.assertRaises(
            ValueError, archive_repositories.get_environment_variables)

    @patch.dict(os.environ, {"GITHUB_ORGANIZATION_NAME": "ministryofjustice"})
    def test_raises_error_when_no_github_token(self):
        self.assertRaises(
            ValueError, archive_repositories.get_environment_variables)

    @patch.dict(os.environ, {"ADMIN_GITHUB_TOKEN": "token"})
    def test_raises_error_when_no_github_organization(self):
        self.assertRaises(
            ValueError, archive_repositories.get_environment_variables)

    @patch.dict(os.environ, {"ADMIN_GITHUB_TOKEN": "token", "GITHUB_ORGANIZATION_NAME": "ministryofjustice"})
    def test_returns_values(self):
        github_token, github_organization_name = archive_repositories.get_environment_variables()
        self.assertEqual(github_token, "token")
        self.assertEqual(github_organization_name, "ministryofjustice")


class TestAddUsersEveryoneGithubTeamGetConfigForOrganization(unittest.TestCase):
    def test_raises_error_when_unknown_github_organization(self):
        self.assertRaises(
            ValueError, archive_repositories.get_config_for_organization, "unknown organization"
        )

    @freeze_time("2021-02-01")
    def test_returns_values_ministryofjustice_config(self):
        last_active_cutoff_date, organization_name, allow_list = archive_repositories.get_config_for_organization(
            "ministryofjustice")
        self.assertEqual(last_active_cutoff_date, datetime.now() -
                         relativedelta(days=0, months=6, years=1))
        self.assertEqual(organization_name, "ministryofjustice")
        self.assertEqual(
            allow_list, archive_repositories.MINISTRYOFJUSTICE_REPOS_ALLOW_LIST)

    @freeze_time("2021-02-01")
    def test_returns_values_moj_analytical_services_config(self):
        last_active_cutoff_date, organization_name, allow_list = archive_repositories.get_config_for_organization(
            "moj-analytical-services")
        self.assertEqual(last_active_cutoff_date, datetime.now() -
                         relativedelta(days=0, months=6, years=1))
        self.assertEqual(organization_name, "moj-analytical-services")
        self.assertEqual(
            allow_list, archive_repositories.MOJ_ANALYTICAL_SERVICES_REPOS_ALLOW_LIST)


if __name__ == "__main__":
    unittest.main()
