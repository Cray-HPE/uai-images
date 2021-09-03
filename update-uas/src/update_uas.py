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

from requests.exceptions import RequestException
import requests

IMAGES_URI = "http://cray-uas-mgr:8088/v1/admin/config/images"
HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}


class UASError(Exception):  # pylint: disable=too-few-public-methods
    """ Exception to report various errors talking to the UAS
    """


def get_registered_images():
    """Get the current set of registered UAI images from the
    UAS.
    """
    response = requests.get(IMAGES_URI, headers=HEADERS,
                            verify=True, timeout=15.0)
    if response.status_code != requests.codes['ok']:
        raise UASError(
            "failed to retrieve configured imagesfrom UAS - %s[%d]" %
            (response.text, response.status_code)
        )
    return response.json()


def find_default_image(images):
    """Search the list of registered images for a defult image, if any.  Return
    the image if found, otherwise None
    """
    for img in images:
        if img['default']:
            print("The default image is currently: '%s'" % img['imagename'])
            return img
    return None


def find_image_by_name(images, img_name):
    """Search the list of registered images for one whose image name is
    'img_name'.  Return the image if found, otherwise None.
    """
    for img in images:
        if img['imagename'] == img_name:
            return img
    return None


def register_image(name, default=False):
    """Register an image by name with UAS
    """
    okay_codes = [requests.codes['created'], requests.codes['ok']]
    params = {
        'default': default,
        'imagename': name,
    }
    response = requests.post(IMAGES_URI, params=params, headers=HEADERS,
                             verify=True, timeout=120.0)
    if response.status_code not in okay_codes:
        raise UASError(
            "failed to register image '%s' default: %s with UAS - %s[%d]" %
            (name, str(default), response.text, response.status_code))
    return 0


def usage(err=None):
    """ Report correct command usage.
    """
    usage_msg = """
update_uas [-d default-image-name] [image-name [image-name ...]]

Where:
    -d default-image-name

       Specifies a candidate default image name from the list of supplied
       image names that will be set if no default is already designated in
       UAS when the command is run.
"""[1:]
    if err:
        sys.stderr.write("%s\n" % err)
    sys.stderr.write(usage_msg)
    return 1


def main(argv):
    """ main entrypoint
    """
    default_image = None
    try:
        opts, args = getopt(argv, "d:")
    except GetoptError as err:
        return usage(err)
    for opt in opts:
        if opt[0] == "-d":
            default_image = opt[1]
    if default_image and default_image not in args:
        return usage(
            "the proposed default image '%s' is not one of the images to "
            "be registered" % default_image
        )
    try:
        images = get_registered_images()
    except (RequestException, UASError) as err:
        print("Waiting for UAS image list failed - %s" % str(err))
        return 1
    retval = 0
    for img in args:
        if find_image_by_name(images, img):
            print("Image named '%s' is already registered, nothing done" % img)
            continue
        # Only make the image default if that was requested and there is no
        # current default image.
        default = (default_image == img and find_default_image(images) is None)
        try:
            register_image(img, default)
        except (RequestException, UASError) as err:
            print("Registering UAS image '%s' failed - %s" % (img, str(err)))
            retval = 1
        print("Registered UAI image '%s', default=%s" % (img, str(default)))
    return retval


# start here
if __name__ == "__main__":   # pragma no unit test
    sys.exit(main(sys.argv[1:]))  # pragma no unit test
