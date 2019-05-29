#!/usr/bin/env python3
"""Create a new box version, creating the box if it doesn't already exist."""

import argparse
import logging
import os
import pdb
import sys

import requests


def parse_arguments():
    """Parse command-line arguments using argparse."""
    parser = argparse.ArgumentParser(description="Create a new box version")
    parser.add_argument("-b", "--box_name", help="The path to the configuration file", required=True)
    parser.add_argument("-v", "--version", help="The logging level to set", required=True)

    return parser.parse_args()

def get_token():
    """Retrieve the Vagrant token from the .token file."""
    pwd = os.path.realpath(os.path.dirname(__file__))
    if not os.path.isfile(os.path.join(pwd, ".token")):
        raise Exception("Token was not specified in .token file.")

    filep = open(os.path.join(pwd, ".token"), "r")
    token = filep.read().strip()

    return token


class VagrantAPI(object):
    """Interact with the Vagrant API."""

    BASE_URL = "https://app.vagrantup.com/api/v1"

    def __init__(self, token):
        """Initialize the object."""
        self.__token = token

        self.__session = self.get_session()

    def get_session(self):
        """Start a Requests session."""
        headers = {
            "Authorization": "Bearer %s" % self.__token,
            "Content-Type": "application/json",
        }
        session = requests.Session()
        session.headers.update(headers)

        return session

    def validate(self):
        """Retrieve box information from the API."""
        url = os.path.join(self.BASE_URL, "authenticate")
        result = self.__session.get(url)
        print(result.text)

        return result

    def create_box(self, box_name):
        """Call the Vagrant API to create the box."""
        url = os.path.join(self.BASE_URL, "boxes")
        data = {
            "box": {
                "username": "broadinstitute",
                "name": box_name,
                "is_private": False,
            }
        }
        result = self.__session.post(url, json=data)

        try:
            result.raise_for_status()
        except requests.HTTPError as exc:
            # 422 means it already exists
            if exc.response.status_code != 422:
                raise exc

        return result

    def create_version(self, user, box_name, version):
        """Call the Vagrant API to create a version of the box."""
        url = os.path.join(self.BASE_URL, "box/%s/%s/versions" % (user, box_name))
        data = {
            "version": {
                "version": version,
            }
        }
        # TODO: Add a description in data
        result = self.__session.post(url, json=data)

        try:
            result.raise_for_status()
        except requests.HTTPError as exc:
            # 422 means it already exists
            if exc.response.status_code != 422:
                raise exc

        return result

    def create_provider(self, user, box_name, version):
        """Call the Vagrant API to create a provider for the version of the box."""
        url = os.path.join(self.BASE_URL, "box/%s/%s/version/%s/providers" % (user, box_name, version))
        data = {
            "provider": {
                "name": "virtualbox",
            }
        }
        result = self.__session.post(url, json=data)

        try:
            result.raise_for_status()
        except requests.HTTPError as exc:
            # 422 means it already exists
            if exc.response.status_code != 422:
                raise exc

        return result

    def prepare_upload(self, user, box_name, version):
        """Call the Vagrant API to retrieve the upload path."""
        url = os.path.join(self.BASE_URL, "box/%s/%s/version/%s/provider/virtualbox/upload" % (user, box_name, version))
        result = self.__session.get(url)

        try:
            result.raise_for_status()
        except requests.HTTPError as exc:
            # 422 means it already exists
            if exc.response.status_code != 422:
                raise exc

        data = result.json()
        if "upload_path" not in data:
            raise Exception("upload_path does not exist in returned data")

        return data["upload_path"]

    def upload_box(self, upload_url):
        """Perform a PUT to the upload_url with the box file to upload the box."""
        files = {"file": open("output-vagrant/package.box", "rb")}

        result = requests.put(upload_url, files=files)
        # This might just work but it returns a requests.exceptions.ConnectionError with .put
        # No idea...
        try:
            result.raise_for_status()
        except requests.HTTPError as exc:
            # 422 means it already exists
            if exc.response.status_code != 422:
                raise exc

        return result

    def release_version(self, user, box_name, version):
        """Call the Vagrant API to release the version."""
        url = os.path.join(self.BASE_URL, "box/%s/%s/version/%s/release" % (user, box_name, version))
        result = self.__session.put(url)

        try:
            result.raise_for_status()
        except requests.HTTPError as exc:
            # 422 means it already exists
            if exc.response.status_code != 422:
                raise exc

        return result


def main():
    """Execute the script."""
    logging.basicConfig(level="DEBUG")
    args = parse_arguments()
    token = get_token()
    vagrant = VagrantAPI(token)
    # vagrant.validate()
    result1 = vagrant.create_box(args.box_name)
    result2 = vagrant.create_version("broadinstitute", args.box_name, args.version)
    result3 = vagrant.create_provider("broadinstitute", args.box_name, args.version)
    upload_url = vagrant.prepare_upload("broadinstitute", args.box_name, args.version)
    try:
        result5 = vagrant.upload_box(upload_url)
    except Exception as exc:
        # Ignore for now...???
        pass
    result4 = vagrant.release_version("broadinstitute", args.box_name, args.version)

    return 0


if __name__ == "__main__":
    RET = main()

    sys.exit(RET)
