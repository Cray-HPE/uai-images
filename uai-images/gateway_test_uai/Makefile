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

GATEWAY_TEST_UAI_IMAGE_NAME ?= cray-uai-gateway-test
GATEWAY_TEST_UAI_DOCKER_ARGS ?= --no-cache --progress plain
VERSION ?= $(shell cat ../../.version)

all: docker

unit_test: docker_test

docker:
	docker build --pull ${GATEWAY_TEST_UAI_DOCKER_ARGS} --tag '${GATEWAY_TEST_UAI_IMAGE_NAME}:${VERSION}' .

# A little bit of a cheat, but building the testing target in the
# dockerfile runs lint, style, and unit tests, so that is how we do
# it.  After that, we don't need the image anymore...
docker_test:
	docker build --pull ${GATEWAY_TEST_UAI_DOCKER_ARGS} --target testing --tag '${GATEWAY_TEST_UAI_IMAGE_NAME}:testing' .
	docker rmi '${GATEWAY_TEST_UAI_IMAGE_NAME}:testing'

# No helm chart for this image
chart_package:
	echo "There is no Helm chart for the Gateway Test UAI image"

clean:
	docker rmi '${GATEWAY_TEST_UAI_IMAGE_NAME}:${VERSION}' || true
