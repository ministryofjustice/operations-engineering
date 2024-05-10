import os
import requests

# Get  credentials from the environment variables
leaver_username = os.getenv("INPUT_LEAVER_USERNAME")
github_token = os.getenv("INPUT_GITHUB_TOKEN")
onepassword_token = os.getenv("INPUT_ONEPASSWORD_TOKEN")
gandi_api_key = os.getenv("INPUT_GANDI_API_KEY")
os_data_hub_api_key = os.getenv("INPUT_OS_DATA_HUB_API_KEY")
docker_api_token = os.getenv("INPUT_DOCKER_API_TOKEN")
sentry_api_token = os.getenv("INPUT_SENTRY_API_TOKEN")
pagerduty_api_token = os.getenv("INPUT_PAGERDUTY_API_TOKEN")
Pingdom_api_token = os.getenv("INPUT_PINGDOM_API_TOKEN")



def remove_from_github():
    headers ={"Authorization": f"Bearer {github_token}"}
    urls = [
         f"https://api.github.com/org/ministryofjustice/members/{leaver_username}",
         f"https://api.github.com/orgs/moj-analytical-services/members/{leaver_username}",
         f"https://api.github.com/orgs/ministryofjustice-test/members/{leaver_username}",
    ]
    for url in urls:
        try:
            response = requests.delete(url, headers=headers)
            response.raise_for_status()
        except requests.exceptions.RequestsException as err:
            print(f"Error: {err}")
        except requests.exceptions.HTTPError as errh:
            print(f"Http Error: {errh}")
        except requests.exceptions.ConnectionError as errc:
            print(f"Error Connecting {errc}")
        except requests.exceptions.Timeout as errt:
            print(f"Timeout Error: {errt}")   
                                                
def remove_from_1password():
    
    headers = {"Authorization": f"Bearer {onepassword_token}"}
    try:
        response = requests.delete(f"https://ministryofjustice.1password.eu/v1/users/{leavers_username}",headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestsException as err:
        print(f"Error: {err}")
    except requests.exceptions.HTTPError as errh:
        print(f"Http Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connectiong {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")  
                  
def remove_from_gandi():
    
    headers = {"Authorization": f"Bearer {gandi_api_key}"}
    try:
        response = requests.delete(f"https://api.gandi.net/v5/domai/users/{leaver_username}", headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as err:
        print(f"Error: {err}")
    except requests.exceptions.HTTPError as errh:
        print(f"Http Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
                                        
def remove_from_os_data_hub():
    
    headers = {"Authorization": f"Bearer {os_data_hub_api_key}"}
    try:
        response = requests.delete(f"https://osdatahub.os.uk/api/v1/users/{leaver_username}",headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as err:
        print(f"Error: {err}")
    except requests.exceptions.HTTPError as errh:
        print(f"Http Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")   
        
def remove_from_docker():
    
    headers = {"Authorization": f"Bearer {docker_api_token}"}
    try:
        response = requests.delete(f"https://docker.com/api/v1/user/{leavers_username}",headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as err:
        print(f"Error: {err}")
    except requests.exceptions.HTTPError as errh:
        print(f"Http Error: {errh}") 
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")

def remove_from_sentry():
    
    headers = {"Authorization": f"Bearer {sentry_api_token}"}
    try:
        response = requests.delete(f"https://sentry.com/api/0/organizations/myorg/members/{leavers_username}", headers=headers)
        response.raise_for_status() 
    except requests.exceptions.RequestsExceptions as err:
        print(f"Error: {err}")
    except requests.exceptions.HTTPError as errh:
        print(f"Http Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}") 
        
def remove_from_pagerduty():
    
    headers = {"Authorization": f"Bearer {pagerduty_api_token}"}
    try:
        response = requests.delete(f"https://api.pagerduty.com/incidents/{incident_id}", headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestsExceptions as err:
        print(f"Error: {err}")
    except requests.exceptions.HTTPError as errh:
        print(f"Http Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")    
        
def remove_pingdom():
    
    headers = {"Authorization" : f"Bearer {pingdom_api_token}"}
    try:
        response = requests.delete(f"https://api.pingdom.com/api/3.1checks/{check_id}", headers=headers)  
        response.raise_for_status()
    except requests.exceptions.RequestsExceptions as err:
        print(f"Error: {err}")
    except requests.exceptions.HTTPError as errh:
        print(f"Http Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")                
                                           
if __name__ == "__main__":
    remove_from_github()
    remove_from_gandi()
    remove_from_os_data_hub()
    remove_from_1password()
    remove_from_docker()
    remove_from_pagerduty()
    remove_from_pingdom()
    
    
    
