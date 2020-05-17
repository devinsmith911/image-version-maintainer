import requests
import semver
import yaml
import argparse
import os.path
import sys
import logging
import re
from requests.auth import HTTPBasicAuth


def parse_versions(version, versions):
    if semver.VersionInfo.isvalid(version):
        ver = semver.VersionInfo.parse(version)
        new_ver_major = check_exists(ver.bump_major(), versions)
        new_ver_minor = check_exists(ver.bump_minor(), versions)
        new_ver_patch = check_exists(ver.bump_patch(), versions)
        if new_ver_major:
            logging.info("New MAJOR version available")
            if fail_on_major:
                logging.info("Exiting 1 due to strict MAJOR version control")
                sys.exit(1)
        if new_ver_minor:
            logging.info("New MINOR version available")
            if fail_on_minor:
                logging.info("Exiting 1 due to strict MINOR version control")
                sys.exit(1)
        if new_ver_patch:
            logging.info("New PATCH version available")
            if fail_on_patch:
                logging.info("Exiting 1 due to strict PATCH version control")
                sys.exit(1)
        if not new_ver_major and not new_ver_minor and not new_ver_patch:
            logging.info("No new versions available")

# Rework this to be much more robust, it should parse using regex to extract just the version tag


def strip_chars(version_string):
    stripped = version_string.strip('v')
    stripped = stripped.split('-')[0]
    return stripped


def check_exists(version_in, versions):
    for version in versions:
        version = strip_chars(version)
        if semver.VersionInfo.isvalid(version):
            version = semver.VersionInfo.parse(version)
            if version == version_in:
                logging.info("New Version detected {}".format(version))
                return True


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


def get_tags(registry_org, registry_repo, api_domain, token):

    headers = {'Authorization': 'Bearer {}'.format(token)}
    try:
        tags_list = requests.get("https://{}/v2/{}/{}/tags/list".format(
            api_domain, registry_org, registry_repo), headers=headers)
        versions = tags_list.json()['tags']
    except Exception:
        logging.error("Error retreiving tags list from registry")
        sys.exit(1)
    return versions

# Write this to parse out versions from compose file


def load_compose(input_file):
    input_file = os.path.abspath(input_file)
    if (os.path.isfile(input_file)):
        image_list = []
        logging.info("Loaded compose file: {}".format(input_file))
        parsed_yaml = yaml.load(open(input_file))
        services = parsed_yaml['services']
        for service in services:
            full_image_tag = (services[service]['image'])
            image_list.append(full_image_tag)
    else:
        logging.error("File {} does not exist".format(input_file))
        sys.exit(1)

    return image_list


def parse_image(image):
    if '/' in image:
        splice = image.split('/')
        org = splice[0]
        repo = splice[1].split(':')[0]
        version = strip_chars(splice[1].split(':')[1])
    else:
        org = 'library'
        repo = image.split(':')[0]
        version = strip_chars(image.split(':')[1])

    return org, repo, version


def main():
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
        parse_versions(version, versions)


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
    main()
