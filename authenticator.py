import requests
import semver
import yaml
import argparse
import os.path
import sys
import logging
import re
from requests.auth import HTTPBasicAuth

def authenticate(registry_username, registry_password, registry_org, registry_repo, auth_domain, auth_service, api_domain):
    if registry_username and registry_password:
        auth = HTTPBasicAuth(registry_username, registry_password)
    # We need to set these to properly authenticate with registry
    auth_scope = "repository:{}/{}:pull".format(
        registry_org, registry_repo)
    auth_offline_token = "1"
    auth_client_id = "shell"
    try:
        get_url = ("https://{}/token?service={}&scope={}&offline_token={}&client_id={}".format(
            auth_domain, auth_service, auth_scope, auth_offline_token, auth_client_id))
        if registry_username and registry_password:
            token_request = requests.get(get_url, auth=auth)
        else:
            token_request = requests.get(get_url)
        token = (token_request.json()['token'])
    except Exception:
        logging.error(
            "Unable to get authentication token, check registry authentication details and urls")
        sys.exit(1)
    return token