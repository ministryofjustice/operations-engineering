import os
from python.services.auth0_service import Auth0Service

def main():
    # Delete all users over 180 days inactive
    auth0_client = Auth0Service(os.getenv("AUTH0_CLIENT_SECRET"), os.getenv(
        "AUTH0_CLIENT_ID"), os.getenv("AUTH0_DOMAIN"), "client_credentials")
    auth0_list = auth0_client.get_inactive_users(days_inactive=180)

    for user in auth0_list:
        auth0_client.delete_user(user["user_id"])


if __name__ == "__main__":
    main()
