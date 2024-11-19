# pylint: disable=wrong-import-order
import os
import boto3
import json
from botocore.exceptions import ClientError

from json import JSONDecodeError


class S3Service:
    def __init__(self, bucket_name: str, organisation_name: str) -> None:
        self.client = boto3.client("s3")
        self.bucket_name = bucket_name
        self.organisation_name = organisation_name

    def _download_file(self, object_name: str, file_path: str):
        self.client.download_file(self.bucket_name, object_name, file_path)
        if not os.path.isfile(file_path):
            raise ValueError(
                f"The {file_path} file did not download or is not in the expected location"
                )

    def _upload_file(self, object_name: str, file_path: str):
        self.client.upload_file(file_path, self.bucket_name, object_name)

    def _delete_file(self, object_name: str):
        self.client.delete_object(Bucket=self.bucket_name, Key=object_name)

    def is_well_known_mta_sts_enforce(self, domain: str) -> bool:
        suffix = ".well-known/mta-sts.txt"
        bucket_name = f"880656497252.{domain}"
        try:
            response = self.client.get_object(Bucket=bucket_name, Key=suffix)
            sts_content = response['Body'].read().decode('utf-8')
            return any(line.startswith("mode: enforce") for line in sts_content.split('\n'))
        except ClientError:
            return False

    def get_json_file(self, object_name: str, file_path: str):

        try:
            with open(file_path, 'wb') as file:
                self.client.download_fileobj(self.bucket_name, object_name, file)
            with open(file_path, 'r', encoding="utf-8") as file:
                mappings = file.read()
            return json.loads(mappings)

        except FileNotFoundError as e:
            raise FileNotFoundError("Error downloading file") from e

        except JSONDecodeError as e:
            raise ValueError("File not in JSON Format") from e
