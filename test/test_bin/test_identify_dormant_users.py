import os
import unittest
from io import StringIO
from unittest.mock import patch

import boto3
from moto import mock_s3

from bin.identify_dormant_github_users import (BOT_USERS_DEEMED_ACCEPTABLE,
                                               download_file_from_s3,
                                               get_usernames_from_csv)


class TestDormantGitHubUsers(unittest.TestCase):

    @mock_s3
    def setUp(self):
        self.bucket = "operations-engineering-dormant-users"
        self.filename = "dormant.csv"
        self.content = """email,username,login\nuser1@example.com,user1,user1\nuser2@example.com,ci-hmcts,user2"""

        conn = boto3.resource('s3', region_name="eu-west-1")
        conn.create_bucket(Bucket=self.bucket)
        conn.Bucket(self.bucket).put_object(
            Key=self.filename, Body=self.content)

    def test_download_file_from_s3(self):
        with patch('sys.stdout', new=StringIO()) as fake_out:
            download_file_from_s3(self.filename)
            self.assertTrue(os.path.isfile(self.filename))
            self.assertIn("downloaded successfully", fake_out.getvalue())
            os.remove(self.filename)

    def test_get_usernames_from_csv(self):
        with open(self.filename, 'w') as f:
            f.write(self.content)

        expected_usernames = ['user1']  # 'ci-hmcts' is in the ignored list
        usernames = get_usernames_from_csv(BOT_USERS_DEEMED_ACCEPTABLE)
        self.assertEqual(usernames, expected_usernames)

        # Clean up by deleting the dummy CSV file
        os.remove(self.filename)


if __name__ == '__main__':
    unittest.main()
