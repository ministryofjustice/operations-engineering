import os
from services.secret_manager_service import SecretsManagerService
from services.pingdom_service import PingdomService


def fetch_aws_secrets():
    region_name = os.getenv('AWS_REGION')
    access_key = os.getenv('AWS_ACCESS_KEY_ID')
    secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')

    secrets_service = SecretsManagerService(
        region_name=region_name,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key
    )

    secret_set_name = "operations-engineering-pingdom-api-key"

    secret_set = secrets_service.get_secret_set(secret_set_name)

    pingdom_api_key = secret_set['operations-engineering-pingdom-api-key-read']

    pingdom_service = PingdomService(api_key=pingdom_api_key)

    pingdom_checks = pingdom_service.get_checks()

    print(f"Pingdom checks received: {pingdom_checks}")


if __name__ == "__main__":
    fetch_aws_secrets()
