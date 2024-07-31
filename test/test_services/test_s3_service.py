# pylint: disable=W0221, C0411
import os
import csv
import json
import tempfile
import unittest
from botocore.exceptions import ClientError
from unittest.mock import call, patch, mock_open
from io import BytesIO
from freezegun import freeze_time
from services.s3_service import S3Service
from config.constants import NO_ACTIVITY


class TestS3Service(unittest.TestCase):
    @patch("services.s3_service.boto3")
    def setUp(self, mock_boto3):
        self.mock_boto3 = mock_boto3
        self.s3_service = S3Service(
            "test-bucket",
            "some-org"
        )
        self.s3_object_file = "s3_object_file.csv"
        self.the_json_file = "the_file.json"
        self.builtins = "builtins.open"
        self.fake_datetime = "2023-01-20T14:51:47.000+01:00"
        self.s3_json_file = "s3_object_file.json"

    def test_download_file_correctly(self):
        # Create a temporary directory
        test_dir = tempfile.mkdtemp()
        # Create a file in the temporary directory
        file_path = os.path.join(test_dir, "the_file.csv")
        with open(file_path, "w", encoding="utf-8") as the_file:
            the_file.write("")

        self.s3_service._download_file(self.s3_object_file, file_path)
        self.mock_boto3.assert_has_calls(
            [call.client("s3"), call.client().download_file(
                "test-bucket", self.s3_object_file, file_path)]
        )

    def test_download_file_raise_error(self):
        self.assertRaises(
            ValueError, self.s3_service._download_file, self.the_json_file, self.s3_json_file)

    def test_upload_file(self):
        self.s3_service._upload_file(self.the_json_file, self.s3_json_file)
        self.mock_boto3.assert_has_calls(
            [call.client("s3"), call.client().upload_file(
                self.s3_json_file, "test-bucket", self.the_json_file)]
        )

    def test_delete_file(self):
        self.s3_service._delete_file(self.s3_json_file)
        self.mock_boto3.assert_has_calls(
            [call.client("s3"), call.client().delete_object(
                Bucket="test-bucket", Key=self.s3_json_file)]
        )

    @patch.object(S3Service, "_delete_file")
    def test_delete_emailed_uses_file(self, mock_delete_file):
        self.s3_service.delete_emailed_users_file()
        mock_delete_file.assert_called_once_with(
            self.s3_service.emailed_users_file_name)

    @patch.object(S3Service, "_upload_file")
    def test_save_emailed_users_file(self, mock_upload_file):
        with patch(self.builtins, mock_open(read_data="data")):
            self.s3_service.save_emailed_users_file(["some-user"])
        mock_upload_file.assert_called_once_with(
            self.s3_service.emailed_users_file_name, self.s3_service.emailed_users_file_path)

    @patch.object(S3Service, "_download_file")
    @patch.object(json, "load")
    def test_get_users_have_emailed(self, mock_json_load, mock_download_file):
        with patch(self.builtins, mock_open(read_data="data")):
            self.s3_service.get_users_have_emailed()
        mock_download_file.assert_called_once_with(
            self.s3_service.emailed_users_file_name, self.s3_service.emailed_users_file_path)
        mock_json_load.assert_called_once()

    @patch.object(S3Service, "_download_file")
    @patch.object(csv, "reader")
    def test_get_users_from_dormant_user_file(self, mock_csv_reader, mock_download_file):
        mock_csv_reader.return_value = tuple(
            [['2012-01-03 10:19:32 +0000', '45574', 'some-user', 'user', '11.34.54.00', 'true', False]])
        users = [
            {
                "username": "some-user",
                "is_outside_collaborator": False,
            }
        ]
        with patch(self.builtins, mock_open(read_data="data")):
            response = self.s3_service.get_users_from_dormant_user_file()
            self.assertEqual(response, users)
        mock_download_file.assert_called_once_with(
            self.s3_service.dormant_users_file_name, self.s3_service.dormant_users_file_path)
        mock_csv_reader.assert_called_once()

    @freeze_time("2023-02-01")
    @patch.object(S3Service, "_get_users_from_org_people_file")
    def test_get_users_from_dormant_user_file_when_not_active(self, mock_get_users_from_org_people_file):
        mock_get_users_from_org_people_file.return_value = [
            {
                "username": "some-user",
                "last_active": "2022-01-20T14:51:47.000+01:00",
            }
        ]

        self.assertEqual(
            self.s3_service.get_active_users_from_org_people_file(), [])

    @freeze_time("2023-02-01")
    @patch.object(S3Service, "_get_users_from_org_people_file")
    def test_get_active_users_from_org_people_file_when_no_activity(self, mock_get_users_from_org_people_file):
        mock_get_users_from_org_people_file.return_value = [
            {
                "username": "some-user",
                "last_active": NO_ACTIVITY,
            }
        ]

        self.assertEqual(
            self.s3_service.get_active_users_from_org_people_file(), [])

    @freeze_time("2023-02-01")
    @patch.object(S3Service, "_get_users_from_org_people_file")
    def test_get_active_users_from_org_people_file_when_active(self, mock_get_users_from_org_people_file):
        mock_get_users_from_org_people_file.return_value = [
            {
                "username": "some-user",
                "last_active": self.fake_datetime,
            }
        ]
        self.assertEqual(
            self.s3_service.get_active_users_from_org_people_file(), ["some-user"])

    @patch.object(S3Service, "_download_file")
    @patch.object(json, "load")
    def test_get_users_from_org_people_file(self, mock_json_load, mock_download_file):
        expected_reply = [
            {
                "username": "some-user",
                "last_active": self.fake_datetime,
            }
        ]
        mock_json_load.return_value = [{"login": "some-user", "name": "some-name", "tfa_enabled": True, "is_public": False,
                                        "role": "Member", "last_active": self.fake_datetime, "saml_name_id": "some-email"}]
        with patch(self.builtins, mock_open(read_data="data")):
            response = self.s3_service._get_users_from_org_people_file()
            self.assertEqual(response, expected_reply)
        mock_download_file.assert_called_once_with(
            self.s3_service.org_people_file_name, self.s3_service.org_people_file_name)

    def test_is_well_known_mta_sts_enforce_enabled(self):
        self.s3_service.client.get_object.return_value = {'Body': BytesIO("mode: enforce".encode('utf-8'))}

        self.assertTrue(self.s3_service.is_well_known_mta_sts_enforce("example.com"))

    def test_is_well_known_mta_sts_enforce_disabled(self):
        self.s3_service.client.get_object.return_value = {'Body': BytesIO("mode: disabled".encode('utf-8'))}

        self.assertFalse(self.s3_service.is_well_known_mta_sts_enforce("example.com"))

    def test_is_well_known_mta_sts_enforce_no_such_key(self):
        self.s3_service.client.get_object.side_effect = ClientError(
            {
                'Error': {
                    'Code': "test"
                }
            },
            operation_name="test"
        )

        self.assertFalse(self.s3_service.is_well_known_mta_sts_enforce("example.com"))


if __name__ == "__main__":
    unittest.main()
