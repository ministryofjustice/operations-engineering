# pylint: disable=W0221, C0411
import os
import tempfile
import unittest
from botocore.exceptions import ClientError
from unittest.mock import call, patch
from io import BytesIO
from services.s3_service import S3Service


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
        test_dir = tempfile.mkdtemp()
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
