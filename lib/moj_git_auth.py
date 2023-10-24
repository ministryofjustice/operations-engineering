import jwt
import time
import requests
from config.logging_config import logging

# This class is used to generate a various GitHub Authentication Tokens


class MoJGitAuth:

    @staticmethod
    def generate_jwt(app_id, private_key):
        """Generate a JWT token for GitHub App

        Args:
            app_id (string): GitHub App ID
            private_key (string): GitHub App Private Key

        Returns:
            string: JWT token
        """
        payload = {
            'iat': int(time.time()),
            'exp': int(time.time()) + 600,
            'iss': app_id
        }
        jwt_token = jwt.encode(payload, private_key, algorithm='RS256')
        return jwt_token

    @staticmethod
    def generate_installation_token(installation_id, jwt_token):
        """Generate an installation token for GitHub App

        Args:
            installation_id (string): GitHub App Installation ID
            jwt_token (string): JWT token

        Returns:
            string: Installation token
        """
        #
        response = requests.post(f'https://api.github.com/app/installations/{installation_id}/access_tokens', headers={
            'Authorization': f'Bearer {jwt_token}',
            'Accept': 'application/vnd.github.machine-man-preview+json'
        })

        if response.status_code == requests.codes.created:
            return response.json()['token']
        else:
            logging.warning(
                f"Failed to get installation token with status code {response.status_code}")

    @staticmethod
    def get_app_install_id(jwt_token):
        headers = {"Authorization": f"Bearer {jwt_token}"}

        response = requests.get(
            "https://api.github.com/app/installations", headers=headers)

        if response.status_code == requests.codes.ok:
            installations = response.json()
            if installations:
                return installations[0]["id"]
        else:
            logging.warning(
                f"Failed to get installations with status code {response.status_code}")
