# Copyright 2021 Hewlett Packard Enterprise Development LP
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
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
# (MIT License)

BASIC_UAI_IMAGE_NAME ?= cray-uai-sles15sp2
BASIC_UAI_DOCKER_ARGS ?= --no-cache --progress plain
VERSION ?= $(shell cat ../../.version)

all: docker

docker:
	docker build --pull ${BASIC_UAI_DOCKER_ARGS} --tag '${BASIC_UAI_IMAGE_NAME}:${VERSION}' .

# No unit test for this image
unit_test:
	echo "There are no unit tests for the basic UAI image."

# No helm chart for this image
chart_package:
	echo "There is no helm chart to package for the basic UAI image."

clean:
	docker rmi '${BASIC_UAI_IMAGE_NAME}:${VERSION}' || true
