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
import requests_mock  # pylint: disable=unused-import
import pytest

from update_uas import (
    IMAGES_URI,
    UASError,
    get_registered_images,
    find_default_image,
    find_image_by_name,
    register_image,
    usage,
    main
)

IMAGES_LIST_NO_DEFAULT = [
    {
        'imagename': 'test_image_1:1.2.3',
        'default': False
    },
    {
        'imagename': 'test_image_2:1.2.3',
        'default': False,
    },
]
IMAGES_LIST_WITH_DEFAULT = [
    {
        'imagename': 'test_image_1:1.2.3',
        'default': False
    },
    {
        'imagename': 'test_image_2:1.2.3',
        'default': True,
    },
]
IMAGES_LIST_EMPTY = [
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
    """Unit test of get_registered_image() with a failed requests.get() call
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


def test_usage():
    """Unit test of the usage() function
    """
    assert usage("some error message") == 1
    assert usage() == 1


# pylint: disable=redefined-outer-name
def test_main_normal(requests_mock):
    """Unit test of the main entrypoint with normal arguments and no failures
    """
    requests_mock.get(IMAGES_URI, text=json.dumps(IMAGES_LIST_NO_DEFAULT))
    requests_mock.post(IMAGES_URI, text="okay")
    args = [
        "-d", "test_image_1",
        IMAGES_LIST_NO_DEFAULT[1]['imagename'],
        "test_image_1",
        "test_image_2",
        "test_image_3"
    ]
    assert main(args) == 0


# pylint: disable=redefined-outer-name
def test_main_no_args(requests_mock):
    """Unit test of the main entrypoint with no arguments and no requests
    failures
    """
    requests_mock.get(IMAGES_URI, text=json.dumps(IMAGES_LIST_NO_DEFAULT))
    requests_mock.post(IMAGES_URI, text="okay")
    assert main([]) == 0


# pylint: disable=redefined-outer-name
def test_main_bad_option(requests_mock):
    """Unit test of the main entrypoint with an unrecognized option
    """
    requests_mock.get(IMAGES_URI, text=json.dumps(IMAGES_LIST_NO_DEFAULT))
    requests_mock.post(IMAGES_URI, text="okay")
    assert main(["-g"]) == 1


# pylint: disable=redefined-outer-name
def test_main_bad_default(requests_mock):
    """Unit test of the main entrypoint with an improper default
    image specified
    """
    requests_mock.get(IMAGES_URI, text=json.dumps(IMAGES_LIST_NO_DEFAULT))
    requests_mock.post(IMAGES_URI, text="okay")
    args = [
        "-d", "bad_imagename",
        IMAGES_LIST_NO_DEFAULT[1]['imagename'],
        "test_image_1",
        "test_image_2",
        "test_image_3"
    ]
    assert main(args) == 1


# pylint: disable=redefined-outer-name
def test_main_fail_get(requests_mock):
    """Unit test of the main entrypoint with a failed requests.get() call
    """
    requests_mock.get(IMAGES_URI, text="expected failure", status_code=404)
    requests_mock.post(IMAGES_URI, text="okay")
    args = [
        "-d", "test_image_1",
        IMAGES_LIST_NO_DEFAULT[1]['imagename'],
        "test_image_1",
        "test_image_2",
        "test_image_3"
    ]
    assert main(args) == 1


# pylint: disable=redefined-outer-name
def test_main_fail_put(requests_mock):
    """Unit test of the main entrypoint with a failed requests.put() call
    """
    requests_mock.get(IMAGES_URI, text=json.dumps(IMAGES_LIST_NO_DEFAULT))
    requests_mock.post(IMAGES_URI, text="expected error", status_code=404)
    args = [
        "-d", "test_image_1",
        IMAGES_LIST_NO_DEFAULT[1]['imagename'],
        "test_image_1",
        "test_image_2",
        "test_image_3"
    ]
    assert main(args) == 1
