import os
import boto3


class S3Service:
    def __init__(self, bucket_name: str) -> None:
        self.client = boto3.client("s3")
        self.bucket_name = bucket_name

    def download_file(self, object_name: str, file_path: str):
        self.client.download_file(
            self.bucket_name, object_name, file_path)
        if not os.path.isfile(file_path):
            raise ValueError(
                f"The {file_path} file did not download or is not in the expected location")

    def upload_file(self, object_name: str, file_path: str):
        self.client.upload_file(file_path, self.bucket_name, object_name)

    def delete_file(self, object_name: str):
        self.client.delete_object(Bucket=self.bucket_name, Key=object_name)
