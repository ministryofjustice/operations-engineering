import unittest
from unittest.mock import Mock, patch
import logging
from github import Github

from python.lib.moj_github import MojGithub


class TestMojGithub(unittest.TestCase):

    @patch.object(Github, 'get_organization')
    def setUp(self, get_org_mock):
        self.org = Mock()
        get_org_mock.return_value = self.org
        self.org_token = "abcde12345"
        self.mojgithub = MojGithub("test_org", self.org_token)

    def test_repos(self):
        self.org.get_repos.return_value = [
            Mock(archived=False, fork=False), Mock(archived=True, fork=False)]
        self.assertEqual(len(self.mojgithub.repos), 6)

    def test_public_repos(self):
        self.org.get_repos.return_value = [
            Mock(archived=False, fork=False), Mock(archived=True, fork=False)]
        self.assertEqual(len(self.mojgithub.public_repos), 2)

    def test_private_repos(self):
        self.org.get_repos.return_value = [
            Mock(archived=False, fork=False), Mock(archived=True, fork=False)]
        self.assertEqual(len(self.mojgithub.private_repos), 2)

    def test_get_unarchived_repos(self):
        self.org.get_repos.return_value = [Mock(archived=False, fork=False, repo_type="public"), Mock(
            archived=True, fork=False, repo_type="private")]
        self.assertEqual(len(self.mojgithub.get_unarchived_repos("all")), 1)
        self.assertEqual(len(self.mojgithub.get_unarchived_repos("public")), 1)
        self.assertEqual(
            len(self.mojgithub.get_unarchived_repos("private")), 1)

    def test_exclude_archived_repos(self):
        repos = [Mock(archived=False, fork=False),
                 Mock(archived=True, fork=False)]
        self.assertEqual(len(self.mojgithub._exclude_archived_repos(repos)), 1)

    def test_exclude_fork_repos(self):
        repos = [Mock(archived=False, fork=False),
                 Mock(archived=False, fork=True)]
        self.assertEqual(len(self.mojgithub._exclude_fork_repos(repos)), 1)
