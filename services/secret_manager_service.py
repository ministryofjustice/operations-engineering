import json
import botocore.session
from botocore.exceptions import ClientError
from aws_secretsmanager_caching import SecretCache, SecretCacheConfig


class SecretsManagerService:
    def __init__(self) -> None:
        client = botocore.session.get_session().create_client('secretsmanager')
        cache_config = SecretCacheConfig()
        self.cache = SecretCache(config=cache_config, client=client)

    def get_secret_set(self, secret_set_name: str):
        try:
            secret_set = json.loads(self.cache.get_secret_string(secret_set_name))
            return secret_set
        except ClientError as error:
            print(f"Error retrieving secret set: {error}")
            return None
