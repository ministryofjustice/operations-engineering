import os
import requests

# Get the credentials from the environment variables
leaver_username = os.gettenv("LEAVER_USERNAME")
github_token = os.getenv("GITHUB_TOKEN")
onepassword_token = os.getenv("ONEPASSWORD_TOKEN")
gandi_api_key = os.getenv("GANDI_API_KEY")
os_data_hub_api_key = os.getenv("OS_DATA_HUB_API_KEY")
google_group_client_id = os.getenv("GOOGLE_GROUPS_CLIENT_ID")
auth0_api_key = os.getenv("AUTH0_API_KEY")

def remove_from_github():
    headers ={"Authorization": f"Bearer {github_token}"}
    response =requests.delete(f"https://api.github.com/org/ministryofjustice/members/{leavers_username}", headers=headers)
    assert response.status_code ==204
    response =requests.delete(f"https://api.github.com/orgs/moj-analytical-services/members/{leavers_username}", headers=headers)
    assert response.status_code ==204
    response =requests.delete(f"https://api.github.com/orgs/ministryofjustice-test/members/{leavers_username}", headers=headers)
    assert response.status_code ==204
    
def remove_from_1password():
    headers = {"Authorization": f"Bearer {onepassword_token}"}
    response = requests.delete(f"https://ministryofjustice.1password.eu/v1/users/{leavers_username}",headers=headers)
    assert response.status_code == 204
    
def remove_from_gandi():
    headers = {"Authorization": f"Bearer {gandi_api_key}"}
    response = requests.delete(f"https://api.gandi.net/v5/domai/users/{leaver_username}", headers=headers)
    assert response.status_code == 204
    
def remove_from_os_data_hub():
    headers = {"Authorization": f"Bearer {os_data_hub_api_key}"}
    response = requests.delete(f"https://osdatahub.os.uk/api/v1/users/{leaver_username}",headers=headers)
    assert response.status_code ==204
    
def remove_from_google_groups():
    headers = {"Authorization": f"Bearer {google_group_client_id}"}
    response = requests.delete(f"https://group.google.com/a/digital.justice.gov.uk/g/opertatioans-engineering/members/{leaver_username}", headers=headers)
    assert response.status_code ==204
    response =requests.delete(f"https://group.google.com/a/digital.justice.gov.uk/g/domain/members{leaver_username}", headers=headers)
    assert response.status_code ==204

def remove_from_auth0():
    headers = {"Authorization": f"Bearer {auth0_api_key}"}
    response = requests.delete(f"https://api_auth0_domain.auth0.com/api/v2/users/{leavers_username}",headers=headers)
    assert response.status_code ==204                   

