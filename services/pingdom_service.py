import requests


class PingdomService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.pingdom.com/api/3.1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
        }

    def get_checks(self):
        url = f"{self.base_url}/checks"
        response = requests.get(url=url, headers=self.headers, timeout=60)

        if response.status_code == 200:
            return response.json()

        return response.raise_for_status()
