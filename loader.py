import requests
import semver
import yaml
import argparse
import os.path
import sys
import logging
import re
from requests.auth import HTTPBasicAuth

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
