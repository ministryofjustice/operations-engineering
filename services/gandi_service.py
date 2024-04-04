import requests


class GandiService:
    def __init__(self, api_key, url_extension) -> None:
        self.headers = {'Authorization': f'ApiKey {api_key}'}
        self.url = "https://api.gandi.net/" + url_extension

    def get_current_account_balance_from_org(self, org_id):
        try:
            response = requests.get(
                url=self.url + org_id, headers=self.headers, timeout=60)
            response.raise_for_status()
            return float(response.json()['prepaid']['amount'])
        except requests.exceptions.HTTPError as authentication_error:
            raise requests.exceptions.HTTPError(
                f"You may need to export your Gandi API key:\n {authentication_error}") from authentication_error
        except TypeError as api_key_error:
            raise TypeError(
                f"Gandi API key does not exist or is in the wrong format:\n {api_key_error}") from api_key_error

