#
# MIT License
#
# (C) Copyright 2022 Hewlett Packard Enterprise Development LP
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
import json
import uuid
import requests_mock  # pylint: disable=unused-import
import pytest

from update_uas import (
    IMAGES_URI,
    CLASSES_URI,
    VOLUMES_URI,
    UASError,
    get_registered_images,
    find_default_image,
    find_image_by_name,
    register_image,
    check_default,
    configure_internal_class,
    update_classes,
    usage,
    entrypoint
)

IMAGES_LIST_NO_DEFAULT = [
    {
        'image_id': 'bab14e88-dca6-4e00-a26a-0115a880d81a',
        'imagename': 'test_image_1:1.2.3',
        'default': False
    },
    {
        'image_id': 'ab1be488-cd6a-e400-2a6a-10518a088da1',
        'imagename': 'test_image_2:1.2.3',
        'default': False,
    },
]
IMAGES_LIST_WITH_DEFAULT = [
    {
        'image_id': 'bab14e88-dca6-4e00-a26a-0115a880d81a',
        'imagename': 'test_image_1:1.2.3',
        'default': False
    },
    {
        'image_id': 'ab1be488-cd6a-e400-2a6a-10518a088da1',
        'imagename': 'test_image_2:1.2.3',
        'default': True,
    },
]
IMAGES_LIST_EMPTY = [
]

CLASSES_LIST = [
    {
        'class_id': '29f7397f-4854-62bd-993f-d6a71fcbd99c',
        'comment': 'nothing of note',
        'default': False,
        'namespace': 'user',
        'opt_ports': None,
        'priority_class_name': 'uai-priority',
        'public_ip': False,
        'uai_compute_network': True,
        'volume_mounts': [],
        'uai_image': {
            'default': True,
            'image_id': 'ab1be488-cd6a-e400-2a6a-10518a088da1',
            'imagename': 'test_image_2:1.2.3',
        },
    },
    {
        'class_id': '2f73997f-4584-26bd-99f3-da71fcb69d9c',
        'comment': 'nothing of note',
        'default': False,
        'namespace': 'user',
        'opt_ports': None,
        'priority_class_name': 'uai-priority',
        'public_ip': False,
        'uai_compute_network': True,
        'volume_mounts': [],
        'uai_image': {
            'default': True,
            'image_id': 'ab1be488-cd6a-e400-2a6a-10518a088da1',
            'imagename': 'test_image_2:1.2.3',
        },
    },
    {
        'class_id': '729f739f-8465-4b2d-99f3-da617cfdbc99',
        'comment': 'nothing of note',
        'default': False,
        'namespace': 'user',
        'opt_ports': None,
        'priority_class_name': 'uai-priority',
        'public_ip': False,
        'uai_compute_network': True,
        'volume_mounts': [],
        'uai_image': {
            'default': False,
            'image_id': 'bab14e88-dca6-4e00-a26a-0115a880d81a',
            'imagename': 'test_image_1:1.2.3'
        },
    },
]

VOLUMES_LIST = [
    {
        "mount_path": "/etc/localtime",
        "volume_description": {
            "host_path": {
                "path": "/etc/localtime",
                "type": "FileOrCreate"
            }
        },
        "volume_id": "60ba2257-7a54-4f5c-8b0f-646f40fee090",
        "volumename": "timezone"
    },
    {
        "mount_path": "/lus",
        "volume_description": {
            "host_path": {
                "path": "/lus",
                "type": "DirectoryOrCreate"
            }
        },
        "volume_id": "a130ae3e-8e87-4bba-816e-8635ba44caf5",
        "volumename": "lustre"
    }
]


# pylint: disable=redefined-outer-name
def test_get_registered_images_success(requests_mock):
    """Unit test of the normal operation of get_registered_image()

    """
    requests_mock.get(IMAGES_URI, text=json.dumps(IMAGES_LIST_NO_DEFAULT))
    images = get_registered_images()
    assert isinstance(images, list)
    assert len(images) == len(IMAGES_LIST_NO_DEFAULT)
    for img in images:
        assert isinstance(img, dict)
        assert img.get('imagename', None) is not None
        assert img.get('default', None) is not None
        assert not img['default']


# pylint: disable=redefined-outer-name
def test_get_registered_images_fail_request(requests_mock):
    """Unit test of get_registered_image() with a failed requests.get()
    call

    """
    requests_mock.get(
        IMAGES_URI,
        text="failed as expected",
        status_code=404
    )
    with pytest.raises(UASError):
        get_registered_images()


# pylint: disable=redefined-outer-name
def test_find_default_image_has_default(requests_mock):
    """Unit test of find_default_image() with a default image present

    """
    requests_mock.get(IMAGES_URI, text=json.dumps(IMAGES_LIST_WITH_DEFAULT))
    images = get_registered_images()
    img = find_default_image(images)
    assert img['imagename'] == IMAGES_LIST_WITH_DEFAULT[1]['imagename']
    assert img['default']


# pylint: disable=redefined-outer-name
def test_find_default_image_no_default(requests_mock):
    """Unit test of find_default_image() with no default image present

    """
    requests_mock.get(IMAGES_URI, text=json.dumps(IMAGES_LIST_NO_DEFAULT))
    images = get_registered_images()
    img = find_default_image(images)
    assert img is None


# pylint: disable=redefined-outer-name
def test_find_image_by_name(requests_mock):
    """Unit test of find_image_by_name() with named image present

    """
    requests_mock.get(IMAGES_URI, text=json.dumps(IMAGES_LIST_NO_DEFAULT))
    images = get_registered_images()
    img = find_image_by_name(
        images,
        IMAGES_LIST_NO_DEFAULT[0]['imagename']
    )
    assert img['imagename'] == IMAGES_LIST_NO_DEFAULT[0]['imagename']


# pylint: disable=redefined-outer-name
def test_find_image_by_name_not_found(requests_mock):
    """Unit test of find_image_by_name() with no such named image present

    """
    requests_mock.get(IMAGES_URI, text=json.dumps(IMAGES_LIST_NO_DEFAULT))
    images = get_registered_images()
    img = find_image_by_name(
        images,
        "non-existent-image"
    )
    assert img is None


# pylint: disable=redefined-outer-name
def test_register_image(requests_mock):
    """Unit test of normal operation of register_image()

    """
    requests_mock.post(IMAGES_URI, text="okay")
    assert register_image("test_name", True) == 0
    assert register_image("test_name", False) == 0


# pylint: disable=redefined-outer-name
def test_register_image_fail(requests_mock):
    """Unit test of register_image() with a failed requests.post() call

    """
    requests_mock.post(IMAGES_URI, text="expected error", status_code=404)
    with pytest.raises(UASError):
        register_image("test_name", True)
    with pytest.raises(UASError):
        register_image("test_name", False)


# pylint: disable=redefined-outer-name
def test_check_default_image_matches_all(requests_mock):
    """Unit test of check_default where the requested default image
    matches both the proposed image and the currently default image.

    """
    requests_mock.get(IMAGES_URI, text=json.dumps(IMAGES_LIST_WITH_DEFAULT))
    images = get_registered_images()  # get an image list with a default in it
    img = images[1]['imagename']  # Pick the default image for the call
    assert check_default(img, img, images)


# pylint: disable=redefined-outer-name
def test_check_default_image_matches_no_current_default(requests_mock):
    """Unit test of check_default where the requested default image is the
    proposed image and there is no current default.

    """
    requests_mock.get(IMAGES_URI, text=json.dumps(IMAGES_LIST_NO_DEFAULT))
    images = get_registered_images()  # Get an image list with no default
    img = images[0]['imagename']  # Pick a random image for the call
    assert check_default(img, img, images)


# pylint: disable=redefined-outer-name
def test_check_default_image_matches_current_default(requests_mock):
    """Unit test of check_default where the requested default image is the
    proposed image and the current default image matches the proposed
    default.

    """
    requests_mock.get(IMAGES_URI, text=json.dumps(IMAGES_LIST_WITH_DEFAULT))
    images = get_registered_images()  # Get an image list with no default
    img_base = images[1]['imagename'].split(':')[0]  # Pick a the default image
    img = "%s:not-the-same-tag" % (img_base)
    assert check_default(img, img, images)


# pylint: disable=redefined-outer-name
def test_check_default_no_requested_default(requests_mock):
    """Unit test of check_default where there is no default image
    requested

    """
    requests_mock.get(IMAGES_URI, text=json.dumps(IMAGES_LIST_WITH_DEFAULT))
    images = get_registered_images()  # get an image list with a default in it
    default = find_default_image(images)  # and use the default image
    img = default['imagename']
    assert not check_default(img, None, images)


# pylint: disable=redefined-outer-name
def test_check_default_image_differs():
    """Unit test of check_default where the proposed default does not
    match the image itself.

    """
    images = IMAGES_LIST_NO_DEFAULT
    assert not check_default("something", "something else", images)


# pylint: disable=redefined-outer-name
def test_configure_internal_class_success(requests_mock):
    """Unit test for configure_internal_class with a successful post
    request

    """
    requests_mock.post(
        CLASSES_URI,
        text=json.dumps(CLASSES_LIST[0])
    )
    volumes = [str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4())]
    comment = "not much to say"
    image_id = str(uuid.uuid4())
    assert configure_internal_class("user", image_id, volumes, comment) == 0


# pylint: disable=redefined-outer-name
def test_configure_internal_class_failure(requests_mock):
    """Unit test for configure_internal_class with a failed post request

    """
    requests_mock.post(
        CLASSES_URI,
        text="expected failure",
        status_code=404
    )
    volumes = [str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4())]
    comment = "not much to say"
    image_id = str(uuid.uuid4())
    with pytest.raises(UASError):
        configure_internal_class("user", image_id, volumes, comment)


# pylint: disable=redefined-outer-name
def test_update_classes_success(requests_mock):
    """Unit test of update_classes with successful patch requests

    """
    requests_mock.patch(
        "%s/%s" % (CLASSES_URI, CLASSES_LIST[0]['class_id']),
        text=json.dumps(CLASSES_LIST[0])
    )
    requests_mock.patch(
        "%s/%s" % (CLASSES_URI, CLASSES_LIST[1]['class_id']),
        text=json.dumps(CLASSES_LIST[1])
    )
    requests_mock.patch(
        "%s/%s" % (CLASSES_URI, CLASSES_LIST[2]['class_id']),
        text=json.dumps(CLASSES_LIST[2])
    )
    images = IMAGES_LIST_WITH_DEFAULT
    classes = CLASSES_LIST
    imagename = 'test_image_1:1.2.3'
    assert update_classes(imagename, images, classes) == 0


# pylint: disable=redefined-outer-name
def test_update_classes_failed(requests_mock):
    """Unit test of update_classes with a failed patch request

    """
    requests_mock.patch(
        "%s/%s" % (CLASSES_URI, CLASSES_LIST[0]['class_id']),
        text="expected failure",
        status_code=404
    )
    requests_mock.patch(
        "%s/%s" % (CLASSES_URI, CLASSES_LIST[1]['class_id']),
        text="expected failure",
        status_code=404
    )
    requests_mock.patch(
        "%s/%s" % (CLASSES_URI, CLASSES_LIST[2]['class_id']),
        text="expected failure",
        status_code=404
    )
    images = IMAGES_LIST_WITH_DEFAULT
    classes = CLASSES_LIST
    imagename = 'test_image_1:1.2.3'
    with pytest.raises(UASError):
        update_classes(imagename, images, classes)


def test_usage():
    """Unit test of the usage() function

    """
    assert usage("some error message") == 1
    assert usage() == 1


# pylint: disable=redefined-outer-name
def test_main_normal(requests_mock):
    """Unit test of the main entrypoint with normal arguments and no
    failures

    """
    requests_mock.get(IMAGES_URI, text=json.dumps(IMAGES_LIST_NO_DEFAULT))
    requests_mock.post(IMAGES_URI, text="okay")
    requests_mock.get(VOLUMES_URI, text=json.dumps(VOLUMES_LIST))
    requests_mock.get(CLASSES_URI, text=json.dumps(CLASSES_LIST))
    requests_mock.post(CLASSES_URI, text="okay")
    for uai_class in CLASSES_LIST:
        requests_mock.patch(
            "%s/%s" % (CLASSES_URI, uai_class['class_id']), text="okay"
        )
    args = [
        "-d", "test_image_1",
        IMAGES_LIST_NO_DEFAULT[1]['imagename'],
        "test_image_1",
        "test_image_2",
        "test_image_3"
    ]
    assert entrypoint(args) == 0


# pylint: disable=redefined-outer-name
def test_main_no_args(requests_mock):
    """Unit test of the main entrypoint with no arguments and no requests
    failures

    """
    requests_mock.get(IMAGES_URI, text=json.dumps(IMAGES_LIST_NO_DEFAULT))
    requests_mock.post(IMAGES_URI, text="okay")
    requests_mock.get(VOLUMES_URI, text=json.dumps(VOLUMES_LIST))
    requests_mock.get(CLASSES_URI, text=json.dumps(CLASSES_LIST))
    requests_mock.post(CLASSES_URI, text="okay")
    for uai_class in CLASSES_LIST:
        requests_mock.patch(
            "%s/%s" % (CLASSES_URI, uai_class['class_id']), text="okay"
        )
    assert entrypoint([]) == 0


# pylint: disable=redefined-outer-name
def test_main_bad_option(requests_mock):
    """Unit test of the main entrypoint with an unrecognized option

    """
    requests_mock.get(IMAGES_URI, text=json.dumps(IMAGES_LIST_NO_DEFAULT))
    requests_mock.post(IMAGES_URI, text="okay")
    requests_mock.get(VOLUMES_URI, text=json.dumps(VOLUMES_LIST))
    requests_mock.get(CLASSES_URI, text=json.dumps(CLASSES_LIST))
    requests_mock.post(CLASSES_URI, text="okay")
    for uai_class in CLASSES_LIST:
        requests_mock.patch(
            "%s/%s" % (CLASSES_URI, uai_class['class_id']), text="okay"
        )
    assert entrypoint(["-g"]) == 1


# pylint: disable=redefined-outer-name
def test_main_bad_default(requests_mock):
    """Unit test of the main entrypoint with an improper default image
    specified

    """
    requests_mock.get(IMAGES_URI, text=json.dumps(IMAGES_LIST_NO_DEFAULT))
    requests_mock.post(IMAGES_URI, text="okay")
    requests_mock.get(VOLUMES_URI, text=json.dumps(VOLUMES_LIST))
    requests_mock.get(CLASSES_URI, text=json.dumps(CLASSES_LIST))
    requests_mock.post(CLASSES_URI, text="okay")
    for uai_class in CLASSES_LIST:
        requests_mock.patch(
            "%s/%s" % (CLASSES_URI, uai_class['class_id']), text="okay"
        )
    args = [
        "-d", "bad_imagename",
        IMAGES_LIST_NO_DEFAULT[1]['imagename'],
        "test_image_1",
        "test_image_2",
        "test_image_3"
    ]
    assert entrypoint(args) == 1


# pylint: disable=redefined-outer-name
def test_main_bad_simple(requests_mock):
    """Unit test of the main entrypoint with an improper simple image
    specified

    """
    requests_mock.get(IMAGES_URI, text=json.dumps(IMAGES_LIST_NO_DEFAULT))
    requests_mock.post(IMAGES_URI, text="okay")
    requests_mock.get(VOLUMES_URI, text=json.dumps(VOLUMES_LIST))
    requests_mock.get(CLASSES_URI, text=json.dumps(CLASSES_LIST))
    requests_mock.post(CLASSES_URI, text="okay")
    for uai_class in CLASSES_LIST:
        requests_mock.patch(
            "%s/%s" % (CLASSES_URI, uai_class['class_id']), text="okay"
        )
    args = [
        "-s", "bad_imagename",
        IMAGES_LIST_NO_DEFAULT[1]['imagename'],
        "test_image_1",
        "test_image_2",
        "test_image_3"
    ]
    assert entrypoint(args) == 1


# pylint: disable=redefined-outer-name
def test_main_bad_broker(requests_mock):
    """Unit test of the main entrypoint with an improper broker image
    specified

    """
    requests_mock.get(IMAGES_URI, text=json.dumps(IMAGES_LIST_NO_DEFAULT))
    requests_mock.post(IMAGES_URI, text="okay")
    requests_mock.get(VOLUMES_URI, text=json.dumps(VOLUMES_LIST))
    requests_mock.get(CLASSES_URI, text=json.dumps(CLASSES_LIST))
    requests_mock.post(CLASSES_URI, text="okay")
    for uai_class in CLASSES_LIST:
        requests_mock.patch(
            "%s/%s" % (CLASSES_URI, uai_class['class_id']), text="okay"
        )
    args = [
        "-b", "bad_imagename",
        IMAGES_LIST_NO_DEFAULT[1]['imagename'],
        "test_image_1",
        "test_image_2",
        "test_image_3"
    ]
    assert entrypoint(args) == 1


# pylint: disable=redefined-outer-name
def test_main_fail_get_images(requests_mock):
    """Unit test of the main entrypoint with a failed requests.get() call
    to get the list of images.

    """
    requests_mock.get(IMAGES_URI, text="expected failure", status_code=404)
    requests_mock.post(IMAGES_URI, text="okay")
    requests_mock.get(VOLUMES_URI, text=json.dumps(VOLUMES_LIST))
    requests_mock.get(CLASSES_URI, text=json.dumps(CLASSES_LIST))
    requests_mock.post(CLASSES_URI, text="okay")
    for uai_class in CLASSES_LIST:
        requests_mock.patch(
            "%s/%s" % (CLASSES_URI, uai_class['class_id']), text="okay"
        )
    args = [
        "-d", "test_image_1",
        IMAGES_LIST_NO_DEFAULT[1]['imagename'],
        "test_image_1",
        "test_image_2",
        "test_image_3"
    ]
    assert entrypoint(args) == 1


# pylint: disable=redefined-outer-name
def test_main_fail_get_volumes(requests_mock):
    """Unit test of the main entrypoint with a failed requests.get() call
    to get the list of volumes.

    """
    requests_mock.get(IMAGES_URI, text=json.dumps(IMAGES_LIST_WITH_DEFAULT))
    requests_mock.post(IMAGES_URI, text="okay")
    requests_mock.get(VOLUMES_URI, text="expected failure", status_code=404)
    requests_mock.get(CLASSES_URI, text=json.dumps(CLASSES_LIST))
    requests_mock.post(CLASSES_URI, text="okay")
    for uai_class in CLASSES_LIST:
        requests_mock.patch(
            "%s/%s" % (CLASSES_URI, uai_class['class_id']), text="okay"
        )
    args = [
        "-d", "test_image_1",
        IMAGES_LIST_NO_DEFAULT[1]['imagename'],
        "test_image_1",
        "test_image_2",
        "test_image_3"
    ]
    assert entrypoint(args) == 1


# pylint: disable=redefined-outer-name
def test_main_fail_get_classes(requests_mock):
    """Unit test of the main entrypoint with a failed requests.get() call
    to get the list of UAI classes.

    """
    requests_mock.get(IMAGES_URI, text=json.dumps(IMAGES_LIST_WITH_DEFAULT))
    requests_mock.post(IMAGES_URI, text="okay")
    requests_mock.get(VOLUMES_URI, text=json.dumps(VOLUMES_LIST))
    requests_mock.get(CLASSES_URI, text="expected failure", status_code=404)
    requests_mock.post(CLASSES_URI, text="okay")
    for uai_class in CLASSES_LIST:
        requests_mock.patch(
            "%s/%s" % (CLASSES_URI, uai_class['class_id']), text="okay"
        )
    args = [
        "-d", "test_image_1",
        IMAGES_LIST_NO_DEFAULT[1]['imagename'],
        "test_image_1",
        "test_image_2",
        "test_image_3"
    ]
    assert entrypoint(args) == 1


# pylint: disable=redefined-outer-name
def test_main_fail_post_image(requests_mock):
    """Unit test of the main entrypoint with a failed requests.post() call
    to post a new image.

    """
    requests_mock.get(IMAGES_URI, text=json.dumps(IMAGES_LIST_NO_DEFAULT))
    requests_mock.post(IMAGES_URI, text="expected error", status_code=404)
    requests_mock.get(VOLUMES_URI, text=json.dumps(VOLUMES_LIST))
    requests_mock.get(CLASSES_URI, text=json.dumps(CLASSES_LIST))
    requests_mock.post(CLASSES_URI, text="okay")
    for uai_class in CLASSES_LIST:
        requests_mock.patch(
            "%s/%s" % (CLASSES_URI, uai_class['class_id']), text="okay"
        )
    args = [
        "-d", "test_image_1",
        IMAGES_LIST_NO_DEFAULT[1]['imagename'],
        "test_image_1",
        "test_image_2",
        "test_image_3"
    ]
    assert entrypoint(args) == 1


# pylint: disable=redefined-outer-name
def test_main_fail_post_internal_class(requests_mock):
    """Unit test of the main entrypoint with a failed requests.put() call
    adding the internal UAI class.

    """
    requests_mock.get(IMAGES_URI, text=json.dumps(IMAGES_LIST_NO_DEFAULT))
    requests_mock.post(IMAGES_URI, text="okay")
    requests_mock.get(VOLUMES_URI, text=json.dumps(VOLUMES_LIST))
    requests_mock.get(CLASSES_URI, text=json.dumps(CLASSES_LIST))
    requests_mock.post(CLASSES_URI, text="expected error", status_code=404)
    for uai_class in CLASSES_LIST:
        requests_mock.patch(
            "%s/%s" % (CLASSES_URI, uai_class['class_id']), text="okay"
        )
    args = [
        "-d", "test_image_1",
        "-s", IMAGES_LIST_WITH_DEFAULT[0]['imagename'],
        "-v", "timezone,lustre",
        IMAGES_LIST_WITH_DEFAULT[0]['imagename'],
        "test_image_1",
        "test_image_2",
        "test_image_3"
    ]
    assert entrypoint(args) == 1


# pylint: disable=redefined-outer-name
def test_main_fail_update_classes(requests_mock):
    """Unit test of the main entrypoint with a failed requests.post() call
    while updating classes.

    """
    requests_mock.get(IMAGES_URI, text=json.dumps(IMAGES_LIST_NO_DEFAULT))
    requests_mock.post(IMAGES_URI, text="okay")
    requests_mock.get(VOLUMES_URI, text=json.dumps(VOLUMES_LIST))
    requests_mock.get(CLASSES_URI, text=json.dumps(CLASSES_LIST))
    requests_mock.post(CLASSES_URI, text="okay")
    for uai_class in CLASSES_LIST:
        requests_mock.patch(
            "%s/%s" % (CLASSES_URI, uai_class['class_id']),
            text="expected error",
            status_code=404
        )
    args = [
        "-d", "test_image_1",
        IMAGES_LIST_WITH_DEFAULT[0]['imagename'],
        "test_image_1",
        "test_image_2",
        "test_image_3"
    ]
    assert entrypoint(args) == 1


# pylint: disable=redefined-outer-name
def test_main_update_classes_image_not_found(requests_mock):
    """Unit test of the main entrypoint with a failed lookup of a
    registered image when updating classes.

    """
    requests_mock.get(IMAGES_URI, text=json.dumps(IMAGES_LIST_NO_DEFAULT))
    requests_mock.post(IMAGES_URI, text="okay")
    requests_mock.get(VOLUMES_URI, text=json.dumps(VOLUMES_LIST))
    requests_mock.get(CLASSES_URI, text=json.dumps(CLASSES_LIST))
    requests_mock.post(CLASSES_URI, text="okay")
    for uai_class in CLASSES_LIST:
        requests_mock.patch(
            "%s/%s" % (CLASSES_URI, uai_class['class_id']), text="okay"
        )
    args = [
        "-d", "test_image_1",
        "-s", "test_image_1",
        "test_image_1",
        "test_image_2",
        "test_image_3"
    ]
    assert entrypoint(args) == 1
