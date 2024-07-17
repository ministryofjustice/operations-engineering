import json
import boto3
from botocore.exceptions import ClientError


class SecretsManagerService:
    def __init__(self, region_name: str, aws_access_key_id: str = None, aws_secret_access_key: str = None) -> None:
        session = boto3.session.Session(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name
        )
        self.secret_manager_client = session.client('secretsmanager')

    def get_secret_set(self, secret_set_name: str) -> str:
        try:
            get_secret_value_response = self.secret_manager_client.get_secret_value(SecretId=secret_set_name)
            secret_set = json.loads(get_secret_value_response['SecretString'])
            return secret_set
        except ClientError as error:
            print(f"Error retrieving secret set: {error}")
