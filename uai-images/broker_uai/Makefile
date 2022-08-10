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
BROKER_UAI_IMAGE_NAME ?= cray-uai-broker
BROKER_UAI_DOCKER_ARGS ?= --no-cache --progress plain
VERSION ?= $(shell cat ../../.version)
ARTIFACTORY_SECRET_FILE ?= ../../secret-file

all: docker

docker:
	DOCKER_BUILDKIT=1 docker build --pull ${BROKER_UAI_DOCKER_ARGS} --secret id=sles,src=${ARTIFACTORY_SECRET_FILE} --tag '${BROKER_UAI_IMAGE_NAME}:${VERSION}' .

# No unit test for this image
unit_test:
	echo "There are no unit tests for the Broker UAI image"

# No helm chart for this image
chart_package:
	echo "There is no Helm chart for the Broker UAI image"

clean:
	docker rmi '${BROKER_UAI_IMAGE_NAME}:${VERSION}' || true
