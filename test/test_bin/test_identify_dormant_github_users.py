from unittest import TestCase

from bin.identify_dormant_github_users import (identify_dormant_github_users,
                                               setup_environment)


class TestIdentifyDormantGithubUsers(TestCase):

    def test_setup_environment(self):
        self.assertEqual(setup_environment(), ('github_token', 'auth0_token'))