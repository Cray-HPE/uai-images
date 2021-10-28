"""
MIT License

(C) Copyright [2021] Hewlett Packard Enterprise Development LP

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.
"""
import sys
from getopt import getopt, GetoptError
from logging import (
    Logger,
    StreamHandler,
    FileHandler,
    DEBUG,
    INFO,
    WARNING,
    ERROR
)

from requests.exceptions import RequestException
import requests

logger = Logger("uas_sanity")

IMAGES_URI = "http://cray-uas-mgr:8088/v1/admin/config/images"
VOLUMES_URI = "http://cray-uas-mgr:8088/v1/admin/config/volumes"
CLASSES_URI = "http://cray-uas-mgr:8088/v1/admin/config/classes"
HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

def wait_for_update_uas(timeout=600):
    """Wait for up to 'timeout' seconds for the update-uas job to
    complete, so we know the UAS configuration is up to date.  Return
    True if it completes in the available time, False if not.

    """
    return True


def get_basic_uai_image(version):
    """Look for a basic UAI image that matches the image version that
    should have been installed by update-uas.  Return image ID of the
    image.

    """
    return None


def get_basic_uai_class(version):
    """Look for a basic UAI class that will be used to test UAI creation
    by UAS.

    """
    return None


def build_test_credentials(user):
    """Build a password entry string that will be used as user credentials
    in the test UAI.

    """
    return "%s:*:10000:10000:Test User:/home/%s:/bin/bash" % (user, user)


def create_ssh_key():
    """Run ssh-keygen to set up a public / private SSH key to use when creating
    and interacting with the test UAI.  Return the public key as a string.

    """
    return None


def launch_test_uai(user):
    """Set up and launch a test uai.  Verify that it shows up in the UAI
    list and that it has a pod in K8s.  Return the unpacked JSON
    description of the UAI.

    """
    return None


def wait_test_uai(uai_id, timeout=600):
    """Wait for the specified UAI to reach a running state. If it does not
    get there in 'timeout' seconds, report the timeout and return False, else
    return True.

    """
    return True


def uai_ssh_test(uai_info):
    """SSH to the test UAI at the specified IP address and run some commands to
    verify that it seems to be working.

    """
    return None


def cleanup(uai_info):
    """Destroy the test UAI based on its IP address, verify that it is
    gone from the UAI list and that the pod, deployment and service
    are gone from K8s.

    """
    return


def main(argv):
    """Main entry point.

    """
    return 0


def __entry_point(argv):
    """Internal entrypoint with exception handling and such.

    """
    return 0


# start here
if __name__ == "__main__":   # pragma no unit test
    sys.exit(__entrypoint(sys.argv[1:]))   # pragma no unit test
