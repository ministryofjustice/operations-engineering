import requests


class GandiService:
    def __init__(self, token, org_id) -> None:
        self.headers = {'Authorization': f'Bearer {token}'}
        self.base_url = "https://api.gandi.net/v5"
        self.org_id = org_id
        self._validate_token()

    def _validate_token(self):
        try:
            validation_url = f"{self.base_url}/organization/organizations/" + self.org_id
            response = requests.get(validation_url, headers=self.headers, timeout=60)
            response.raise_for_status()
        except requests.exceptions.HTTPError as http_error:
            if http_error.response.status_code in [401, 403]:
                error_message = {"Invalid API token provided. {http_error}"}
                raise ValueError(error_message)

    def get_current_account_balance_from_org(self):
        response = requests.get(url=self.base_url + "/billing/info/" + self.org_id, headers=self.headers, timeout=60)
        response.raise_for_status()
        return float(response.json()['prepaid']['amount'])
