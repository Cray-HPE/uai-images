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
import json  # pylint: disable=unused-import
import uuid  # pylint: disable=unused-import
import requests_mock  # pylint: disable=unused-import
import pytest  # pylint: disable=unused-import

from uas_sanity_test import (
    IMAGES_URI,
    CLASSES_URI,
    wait_for_update_uas,
    get_basic_uai_image,
    get_basic_uai_class,
    build_test_credentials,
    create_ssh_key,
    launch_test_uai,
    wait_test_uai,
    uai_ssh_test,
    cleanup,
    __entry_point,
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


# pylint: disable=redefined-outer-name
def test_something(requests_mock):
    """Placeholder for a test

    """
    requests_mock.get(IMAGES_URI, text=json.dumps(IMAGES_LIST_NO_DEFAULT))
    requests_mock.get(CLASSES_URI, text=json.dumps(CLASSES_LIST))
    wait_for_update_uas(1)
    get_basic_uai_image('x.x.x')
    get_basic_uai_class('x.x.x')
    build_test_credentials('x.x.x')
    create_ssh_key()
    uai_info = launch_test_uai('test_user')
    wait_test_uai('blah', 1)
    uai_ssh_test(uai_info)
    cleanup(uai_info)
    __entry_point([])
