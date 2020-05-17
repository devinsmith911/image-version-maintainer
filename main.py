import requests
import semver
import yaml
import argparse
import os.path
import sys
import logging
import re
from requests.auth import HTTPBasicAuth
from loader import load_compose
from parser import parse_image, get_tags, parse_versions
from authenticator import authenticate 

def main(fail_on_major,fail_on_minor,fail_on_patch):
    # Set logging
    logging.basicConfig(format='%(levelname)s: %(message)s', level=log_level)

    # Load images from compose file specified
    images = load_compose(compose_file)

    # Loop to check image by image
    for image in images:
        logging.info("Checking if {} is the latest version...".format(image))

        # Parse out image information
        org, repo, version = parse_image(image)

        # Generate token to authenticate call to registry
        token = authenticate(registry_username, registry_password, org, repo,
                             registry_auth_domain, registry_auth_service, registry_api_domain)

        # Get the full list of versions from the tag list
        versions = get_tags(org, repo, registry_api_domain, token)

        # Parse the versions and see if a newer one exists
        parse_versions(version, versions,fail_on_major,fail_on_minor,fail_on_patch)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument('--compose-file', action='store',
                        dest='compose_file', required=True,
                        help='Compose file to process')

    parser.add_argument('--registry-username', action='store', required=False,
                        dest='registry_username', default='',
                        help='Set user for registry to authenticate against')

    parser.add_argument('--registry-password', action='store', required=False,
                        dest='registry_password', default='',
                        help='Set password for registry to authenticate against')

    parser.add_argument('--registry-auth-domain', action='store', required=False,
                        dest='registry_auth_domain', default='auth.docker.io',
                        help='Set the auth domain for registry')

    parser.add_argument('--registry-auth-service', action='store', required=False,
                        dest='registry_auth_service', default='registry.docker.io',
                        help='Set auth service for registry')

    parser.add_argument('--registry-api-domain', action='store', required=False,
                        dest='registry_api_domain', default='registry-1.docker.io',
                        help='Set auth domain for registry api')

    parser.add_argument('--log-level', action='store',
                        dest='log_level', default='info',
                        help='Logging level')

    parser.add_argument('--major',  action='store_true',
                        dest='fail_on_major', default=False, required=False,
                        help='Exit 1 if there is new major version available')

    parser.add_argument('--minor', action='store_true',
                        dest='fail_on_minor', default=False, required=False,
                        help='Exit 1 if there is new minor version available')

    parser.add_argument('--patch', action='store_true',
                        dest='fail_on_patch', default=False, required=False,
                        help='Exit 1 if there is new patch version available')

    parsed = parser.parse_args()
    compose_file = parsed.compose_file
    fail_on_major = parsed.fail_on_major
    fail_on_minor = parsed.fail_on_minor
    fail_on_patch = parsed.fail_on_patch
    registry_username = parsed.registry_username
    registry_password = parsed.registry_password
    registry_auth_domain = parsed.registry_auth_domain
    registry_auth_service = parsed.registry_auth_service
    registry_api_domain = parsed.registry_api_domain
    log_level = parsed.log_level.upper()
    main(fail_on_major,fail_on_minor,fail_on_patch)
