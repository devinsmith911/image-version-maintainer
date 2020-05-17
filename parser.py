import requests
import semver
import yaml
import argparse
import os.path
import sys
import logging
import re
from requests.auth import HTTPBasicAuth

def check_exists(version_in, versions):
    for version in versions:
        version = strip_chars(version)
        if semver.VersionInfo.isvalid(version):
            version = semver.VersionInfo.parse(version)
            if version == version_in:
                logging.info("New Version detected {}".format(version))
                return True

def strip_chars(version_string):
    stripped = version_string.strip('v')
    stripped = stripped.split('-')[0]
    return stripped

def parse_versions(version, versions,fail_on_major,fail_on_minor,fail_on_patch):
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