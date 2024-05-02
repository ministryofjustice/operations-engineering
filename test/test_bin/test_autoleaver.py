import requests
import unittest
from unittest.mock import patch

class LeaverProcess:
    def __init__(self,name):
        self.name =name
        self.headers = {'Authorization': 'github_token'}
    
    def revoke_github_access(self):
        response = requests.delete(f"https://api.github.com/org/org/members/{self.name}", headers=self.headers)
        return response.status_code
    
    def revoke_gandi_access(self):
        api_key ='need to input api key'
        user_email= self.name
        
        url = f"https://api.gandi.net/v5/organisation/{organisation_id}/members/{user_email}"
        headers = {
            'Authorization': f'Apikey {api_key}',
            'content-Type': 'application/json'
        }
        try:
            response = requests.delete(url, headers=headers)
            return response.status_code
        except Exception as e:
            print(f"Revoking access from Gandi.net: {e}")
            return None
    def revoke_osdatahub_access(self):
        api_key = 'need to input api key'
        user_email= self.name
        
        url =f"https://api.osdatahub.os.uk/v0/users/{user-email}/revoke-access"
        headers = {
            'Authorization': f'Apikey {api_key}',
            'content-Type': 'application/json'
        }
        try:
            response = requests.delete(url, headers=headers)
            return response.status_code
        except Exception as e:
            print(f"Revoking access from OS DataHub: {e}")
            return None
    def revoke_1password_access(self):
        api_key = 'need to input api key'
        user_email = self.name
        
        url=f"https://api.1.password.com/v1/users/{user_email}/revoke-access"
        headers = {
            'Authorization': f'ApiKey {api_key}',
            'content-Type': 'application/json'
        } 
        try:
            response = requests.post(url, headers=headers)
            return response.status_code
        except Exception as e:
            print(f"Revoking access from 1 Password: {e}")
            return None
    def revoke_pagerduty_access(self):
        api_key = 'need to input api key'
        user_email = self.name
        
        url = f"https://api.1.pagerduty.com/users{user_email}/revoke-access"
        headers ={
            'Authorization': f'ApiKey {api_key}',
            'content-Type': 'application/json'
        }
        try:
            response =requests.post(url,headers=headers)
            return response.statusd_code
        except Exception as e:
            print(f"Revoking access from PagerDuty: {e}")
            return None
class TestLeaverprocess(unittest.TestCase):
    def setup(self):
        self.leaver_process = LeaverProcess()
        
    def test_revoke_operations_engineering_access(self):
        # Test to revoke_operational_engineering_access method
        # placeholder as the actual test will depend

    def test_process_leaver(self):
        # Test the process_leaver method
        # This is a placeholder actual test will depend on implementation

    if __name__ == "__main__":
    unittest.main()     