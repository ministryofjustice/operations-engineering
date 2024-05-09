import unittest
from unittest.mock import patch, Mock
import os
import test_autoleaver

class TestRemoveService(unittest.TestCase):
    @patch('requests.delete')
    @patch.dict(os.environ, {
        "INPUT_LEAVER_USERNAME": "test_user",
        "INPUT_GITHUB_TOKEN": "github_token",
        "INPUT_ONEPASSWORD_TOKEN": "onepassword_token",
        "INPUT_GANDI_API_KEY": "gandi_api_key",
        "INPUT_os_DATA_HUB_API_KEY": "os_data_hub_api_key"
    })
    def test_remove_from_github(self, mock_delete):
        mock_response =Mock()
        mock_response.raise_for_status.return_value = None
        mock_delete.return_value = mock_response
        
        your_script.remove_from_github()
        
        excepted_calls = [
            call(f"https://api.github.com/org/ministryofjustice/test_user", headers={"Authorization": "Bearer github_token"}),
            call(f"https://api.github.com/org/moj-analytical-service/members/test_user", headers={"Authorization": "Bearer github_token"}),
            call(f"https://api.github.com/org/ministryofjustice-test/members/test_user",headers={"Authorization": "Bearer github_token"}),
        ] 
        mock_delete.assert_has_calls(expected_calls, any_order=True)
    
    def test_remove_from_1password(self, mock_delete):
        mock_response =Mock()
        mock_response.raise_for_status.return_value = None
        mock_delete.return_value = mock_response
        
        your_script.remove_from_1password()
        
        mock_delete.assert_called_once_with(
            f"https://ministryofjustice.1password.eu/v1/users/test-user",
            headers={"Authorization": "Bearer onepassword_token"}
        ) 
    def test_remove_from_gandi(self, mock_delete):
        mock_response =Mock()
        mock_response.raise_for_status.return_value = None
        mock_delete.return_value = mock_response
        
        your_script.remove_from_gandi()
        
        mock_delete.assert_called_once_with(
            f"https://api.gandi.net/v5/domain/users/test_user"
            headers={"Authorization": "bearer gandi_api_key"}
        )
    def test_remove_from_os_data_hub(self, mock_delete):
        mock_response =Mock()
        mock_response.raise_for_status.return_value = None
        mock_delete.return_value = mock_response
        
        your_script.remove_from_os_data_hub()
        
        mock_delete.assert_calles_once_with(
            f"https://osdatahub.os.uk/api/v1/users/test_user",
            headers={"Authorization": "Bearer os_data_hub_api_key"}
        )
if __name__ == '_mai_':
    unittest.main()                       
        
               
        
                     