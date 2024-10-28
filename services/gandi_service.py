import requests


class GandiService:
    def __init__(self, token, org_id) -> None:
        self.headers = {'Authorization': f'Bearer {token}'}
        self.base_url = "https://api.gandi.net/v5"
        self.org_id = org_id
        self._validate_token()

    def _validate_token(self):
        validation_url = f"{self.base_url}/organization/organizations/" + self.org_id
        response = requests.get(validation_url, headers=self.headers, timeout=60)
        response.raise_for_status()

    def get_current_account_balance_from_org(self):
        response = requests.get(url=self.base_url + "/billing/info/" + self.org_id, headers=self.headers, timeout=60)
        response.raise_for_status()
        return float(response.json()['prepaid']['amount'])
