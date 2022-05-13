#
# MIT License
#
# (C) Copyright 2021-2022 Hewlett Packard Enterprise Development LP
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
import sys
from getopt import getopt, GetoptError

from requests.exceptions import RequestException
import requests

IMAGES_URI = "http://cray-uas-mgr:8088/v1/admin/config/images"
VOLUMES_URI = "http://cray-uas-mgr:8088/v1/admin/config/volumes"
CLASSES_URI = "http://cray-uas-mgr:8088/v1/admin/config/classes"
HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

SIMPLE_UAI_CLASS_COMMENT = (
    "HPE Provided Simple UAI Class -- Please Do Not Delete or Modify"
)


class UASError(Exception):  # pylint: disable=too-few-public-methods
    """ Exception to report various errors talking to the UAS
    """


class UsageError(Exception):  # pylint: disable=too-few-public-methods
    """ Exception to report usage problems in parameter processing
    """


class ContextualError(Exception):  # pylint: disable=too-few-public-methods
    """ Exception to report failures seen and contextualized in the main
    function.
    """


def get_registered_images():
    """Get the current set of registered UAI images from the
    UAS.
    """
    response = requests.get(IMAGES_URI, headers=HEADERS,
                            verify=True, timeout=15.0)
    if response.status_code != requests.codes['ok']:
        raise UASError(
            "failed to retrieve configured images from UAS - %s[%d]" %
            (response.text, response.status_code)
        )
    return response.json()


def get_volume_ids(volumenames):
    """Get the list of volume_ids for the specified list of volume names
    (if they are configured) in the UAS configuration.  If a volume
    name is not configured, there is no corresponding volume_id so
    ignore it.

    """
    response = requests.get(VOLUMES_URI, headers=HEADERS,
                            verify=True, timeout=15.0)
    if response.status_code != requests.codes['ok']:
        raise UASError(
            "failed to retrieve configured volumes from UAS - %s[%d]" %
            (response.text, response.status_code)
        )
    # On successm the above returns a list of volumes, each with a
    # 'volumename' and a 'volume_id'.  We want the volume_ids of the
    # ones that are in the basic_volumnames list.
    volumes = response.json()
    return [
        volume['volume_id']
        for volume in volumes
        if volume['volumename'] in volumenames
    ]


def get_uai_classes():
    """Get the current set of UAI classes from the UAS.
    """
    response = requests.get(CLASSES_URI, headers=HEADERS,
                            verify=True, timeout=15.0)
    if response.status_code != requests.codes['ok']:
        raise UASError(
            "failed to retrieve configured UAI classes from UAS - %s[%d]" %
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
            (name, str(default), response.text, response.status_code)
        )
    return 0


def check_default(img, default_img, images):
    """The current image ('img') should be set as default if it is the
    proposed default image ('default_img'), and there is no current
    default image or the current default image has the same image name
    base (ignoring the tag) as the proposed default image.

    """
    if default_img is None:
        return False
    if img != default_img:
        return False
    cur_default = find_default_image(images)
    cur_default_name = cur_default['imagename'] if cur_default else None
    cur_default_base = cur_default_name.split(':')[0] if cur_default else None
    default_base = default_img.split(':')[0]
    return cur_default is None or default_base == cur_default_base


def configure_internal_class(namespace, image_id, volumes, comment):
    """Configure a UAI class that is only internally reachable and HPE
    supplied.

    """
    okay_codes = [requests.codes['created'], requests.codes['ok']]
    params = {
        'comment': comment,
        'image_id': image_id,
        'public_ip': False,
        'volume_list': volumes,
        'uai_compute_network': True,
        'namespace': namespace,
        'default': False,
        'resource_id': None,
        'uai_creation_class': None,
        'opt_ports': None,
        'priority_class_name': None,
    }
    response = requests.post(CLASSES_URI, params=params, headers=HEADERS,
                             verify=True, timeout=120.0)
    if response.status_code not in okay_codes:
        raise UASError(
            "failed to configure class '%s' with UAS - %s[%d]" %
            (comment, response.text, response.status_code)
        )
    return 0


def update_classes(image_name, images, classes):
    """Look for UAI classes that create UAIs with images having the
    same base-name as the specified image and update them to use the
    specified image.

    """
    okay_codes = [requests.codes['created'], requests.codes['ok']]
    image = find_image_by_name(images, image_name)
    if image is None:
        print(
            "WARNING: updating classes: image '%s' not found in %s -- "
            "should only happen during unit testing, never in production" %
            (image_name, str(images))
        )
        return 0
    image_id = image['image_id']
    basename = image_name.split(':')[0]
    id_list = [image['image_id'] for image in images
               if basename == image['imagename'].split(':')[0]]
    matching_class_ids = [uai_class['class_id'] for uai_class in classes
                          if uai_class['uai_image']['image_id'] in id_list]
    for class_id in matching_class_ids:
        params = {'image_id': image_id}
        uri = "%s/%s" % (CLASSES_URI, class_id)
        response = requests.patch(uri, params=params, headers=HEADERS,
                                  verify=True, timeout=120.0)
        if response.status_code not in okay_codes:
            raise UASError(
                "failed to update image id in class '%s' to '%s' - %s[%d]" %
                (class_id, image_id, response.text, response.status_code)
            )
    return 0


def usage(err=None):
    """ Report correct command usage.
    """
    usage_msg = """
update_uas [-d image-name] [-s image-name] -v [volume-list] [image-name [...]]

Where:
    -s image-name

       Specifies the name of the image to be registered for use in a
       simple UAI for sanity testing UAS.  The image-name must be in
       the list of image-names specified in the arguments.

    -d image-name

       Specifies a candidate default image name from the list of
       supplied image names that will be set if no default is already
       designated in UAS when the command is run.  The image-name must
       be in the list of image-names specified in the arguments.

    -v volume-list

       Specifies a comma separated list of volume names to be
       configured into a simple UAI class provided for sanity testing
       UAS.  These will be used only if they are configured, no
       volumes will be added, and it is not an error to request a
       volume name that is unknown to UAS.
"""[1:]
    if err:
        sys.stderr.write("%s\n" % err)
    sys.stderr.write(usage_msg)
    return 1


def cmdline(argv):
    """Parse arguments and return settings.  Raise a usage error if there is
    a problem.
    """
    default_img_nm = None
    simple_img_nm = None
    simple_volnames = ["timezone", "lustre"]
    try:
        opts, args = getopt(argv, "s:d:v:")
    except GetoptError as err:
        raise UsageError from err
    for opt in opts:
        if opt[0] == "-d":
            default_img_nm = opt[1]
        if opt[0] == "-v":
            simple_volnames = opt[1].split(',')
        if opt[0] == "-s":
            simple_img_nm = opt[1]
    if default_img_nm and default_img_nm not in args:
        raise UsageError(
            "the proposed default image '%s' is not one of the images to "
            "be registered" % default_img_nm
        )
    if simple_img_nm and simple_img_nm not in args:
        raise UsageError(
            "the proposed simple UAI image '%s' is not one of the images to "
            "be registered" % simple_img_nm
        )
    return (default_img_nm, simple_img_nm, simple_volnames, args)


def main(argv):
    """ main entrypoint
    """
    retval = 0
    default_img_nm, simple_img_nm, simple_volnames, args = cmdline(argv)
    try:
        images = get_registered_images()
    except (RequestException, UASError) as err:
        raise ContextualError from err
    try:
        simple_volumes = get_volume_ids(simple_volnames)
    except (RequestException, UASError) as err:
        raise ContextualError from err
    try:
        uai_classes = get_uai_classes()
    except (RequestException, UASError) as err:
        raise ContextualError from err
    for img in args:
        if find_image_by_name(images, img):
            print("Image named '%s' is already registered, nothing done" % img)
            continue
        default = check_default(img, default_img_nm, images)
        try:
            register_image(img, default)
        except (RequestException, UASError) as err:
            print("Registering UAS image '%s' failed - %s" % (img, str(err)))
            retval = 1
            continue
        print("Registered UAI image '%s', default=%s" % (img, str(default)))
    # We (may) have registered new images, so get the up-to-date list
    # from the UAS to use from here on in.
    images = get_registered_images()

    # If an image name was given for a simple UAI class, make the
    # simple UAI class.
    if simple_img_nm:
        simple_image = find_image_by_name(images, simple_img_nm)
        if not simple_image:
            raise ContextualError(
                "Cannot find simple image '%s' in UAS config"
            )
        try:
            configure_internal_class(
                namespace="user",
                image_id=simple_image['image_id'],
                volumes=simple_volumes,
                comment=SIMPLE_UAI_CLASS_COMMENT
            )
        except (RequestException, UASError) as err:
            raise ContextualError from err

    # Go through the newly registered images and update any classes
    # that are using images with the same base name as the new ones to
    # use the new ones.
    for img in args:
        try:
            update_classes(img, images, uai_classes)
        except (RequestException, UASError) as err:
            print(
                "Failed to update classes using images similar to '%s' - %s" %
                (img, str(err))
            )
            retval = 1
    if retval != 0:
        raise ContextualError(
            "Errors detected during update see details above"
        )
    return 0


def entrypoint(argv):
    """ Entrypoint function to handle exceptions from main and turn them into
    return codes and error reports that will, eventually, become exit status.
    """
    try:
        return main(argv)
    except UsageError as err:
        usage(str(err))
        return 1
    except ContextualError as err:
        print(str(err))
        return 1


# start here
if __name__ == "__main__":   # pragma no unit test
    sys.exit(entrypoint(sys.argv[1:]))   # pragma no unit test
