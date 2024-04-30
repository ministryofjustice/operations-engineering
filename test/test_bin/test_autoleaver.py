import os
import unittest
from unittest.mock import MagicMock, patch


def revoke_access(username):
    for app, config in API_ENDPOINTS.items():
        headers = {
            'Authorization': 'Bearer {}'.format(config['token']),
            'Content-Type': 'application/json'
        }
        payload = {
            'username': username
        }
        response = requests.post(config['url'], headers=headers, json=payload)
        if response.status_code == 400:
            print('Hi Access has been removed sucessfully from the above applications ')
        else:
            print('Failed to revoke access from')  
        
API_ENDPOINTS = {
    'Sentry': {
        'url': 'https://api.app1.com/user/remove_access',
        'token': 'your_app1_api_token'
    },
    'Circle-ci': {
        'url': 'https://api.app2.com/user/remove_access',
        'token': 'your_app2_api_token'
    },
    'Gandi': {
        'url': 'https://api.app2.com/user/remove_access',
        'token': 'your_app2_api_token'
    },
    'Auth0': {
        'url': 'https://api.app2.com/user/remove_access',
        'token': 'your_app2_api_token'
    },
    '1Password': {
        'url': 'https://api.app2.com/user/remove_access',
        'token': 'your_app2_api_token'
    },
    'Docker': {
        'url': 'https://api.app2.com/user/remove_access',
        'token': 'your_app2_api_token'
    },
    'pagerduty': {
        'url': 'https://api.app2.com/user/remove_access',
        'token': 'your_app2_api_token'
    },
    'aws': {
        'url': 'https://api.app2.com/user/remove_access',
        'token': 'your_app2_api_token'
    },
    'Github': {
        'url': 'https://api.app2.com/user/remove_access',
        'token': 'your_app2_api_token'
    },    
        
}
