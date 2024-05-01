import requests
import unittest

class LeaverProcess:
    def revoke_operations_engineering_access(self, github_username, one_password_email):
        # Use GitHub API to remove user from organisations
        github_api_url = "https://api.github.com/orgs/MOJ/memberships/" + github_username
        headers = {"Authorization": "Bearer YOUR_GITHUB_TOKEN"}
        response = requests.delete(github_api_url, headers=headers)
        if response.status_code !=204:
            raise Exception("Failed to remove user from organisation")
        # Need to use 1Password API to remove user
        # 
        #
        def process_leaver(self, github_username, one_password_email):
            self.revoke_operations_engineering_access(github_username, one_password_email)

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
             
                   
        
