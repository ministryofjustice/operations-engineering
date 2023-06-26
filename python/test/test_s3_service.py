import os
import tempfile
import unittest
from unittest.mock import call, patch
from python.services.s3_service import S3Service


class TestS3Service(unittest.TestCase):
    # pylint: disable=R6301
    @patch("python.services.s3_service.boto3")
    def test_download_file_correctly(self, mock_boto3):
        # Create a temporary directory
        test_dir = tempfile.mkdtemp()
        # Create a file in the temporary directory
        file_path = os.path.join(test_dir, "the_file.csv")
        with open(file_path, "w", encoding="utf-8") as the_file:
            the_file.write("")

        s3_service = S3Service(
            "test-bucket"
        )
        s3_service.download_file("s3_object_file.csv", file_path)
        mock_boto3.assert_has_calls(
            [call.client("s3"), call.client().download_file(
                "test-bucket", "s3_object_file.csv", file_path)]
        )

    # pylint: disable=W0613
    @patch("python.services.s3_service.boto3")
    def test_download_file_raise_error(self, mock_boto3):
        s3_service = S3Service(
            "test-bucket"
        )

        self.assertRaises(
            ValueError, s3_service.download_file, "the_file.json", "s3_object_file.json")

    # pylint: disable=R6301
    @patch("python.services.s3_service.boto3")
    def test_upload_file(self, mock_boto3):
        s3_service = S3Service(
            "test-bucket"
        )
        s3_service.upload_file("the_file.json", "s3_object_file.json")
        mock_boto3.assert_has_calls(
            [call.client("s3"), call.client().upload_file(
                "s3_object_file.json", "test-bucket", "the_file.json")]
        )

    # pylint: disable=R6301
    @patch("python.services.s3_service.boto3")
    def test_delete_file(self, mock_boto3):
        s3_service = S3Service(
            "test-bucket"
        )
        s3_service.delete_file("s3_object_file.json")
        mock_boto3.assert_has_calls(
            [call.client("s3"), call.client().delete_object(
                Bucket="test-bucket", Key="s3_object_file.json")]
        )


if __name__ == "__main__":
    unittest.main()
