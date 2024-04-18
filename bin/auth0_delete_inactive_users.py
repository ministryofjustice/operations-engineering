import os

from services.auth0_service import Auth0Service


def delete_inactive_users(auth0_client: Auth0Service):
    # Delete all users over 180 days inactive
    auth0_list = auth0_client.get_inactive_users(days_inactive=180)

    for user in auth0_list:
        auth0_client.delete_user(user["user_id"])


def get_auth0_client_details() -> tuple[str, str, str]:
    client_secret = os.getenv('AUTH0_CLIENT_SECRET')
    client_id = os.getenv('AUTH0_CLIENT_ID')
    domain = os.getenv('AUTH0_DOMAIN')

    if not all([client_secret, client_id, domain]):
        raise ValueError(
            'Required environment variables AUTH0_CLIENT_SECRET, AUTH0_CLIENT_ID, or AUTH0_DOMAIN are not set')

    return client_secret, client_id, domain


def main():
    auth0_client_secret, auth0_client_id, auth0_domain = get_auth0_client_details()

    auth0_client = Auth0Service(
        client_secret=auth0_client_secret,
        client_id=auth0_client_id,
        domain=auth0_domain,
        grant_type="client_credentials"
    )
    delete_inactive_users(auth0_client)


if __name__ == "__main__":
    main()
