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

UPDATE_UAS_CHART_NAME ?= update-uas
UPDATE_UAS_CHART_VERSION ?= $(shell cat ../.version)
UPDATE_UAS_IMAGE_NAME ?= update-uas
UPDATE_UAS_DOCKER_ARGS ?= --no-cache --progress plain
HELM_UNITTEST_IMAGE ?= quintush/helm-unittest:3.3.0-0.2.5
VERSION ?= $(shell cat ../.version)

all: unit_test docker chart_package

unit_test: docker_test chart_test

docker:
	docker build --pull ${UPDATE_UAS_DOCKER_ARGS} --tag '${UPDATE_UAS_IMAGE_NAME}:${VERSION}' .

# A little bit of a cheat, but building the testing target in the
# dockerfile runs lint, style, and unit tests, so that is how we do
# it.  After that, we don't need the image anymore...
docker_test:
	docker build --pull ${UPDATE_UAS_DOCKER_ARGS} --target testing --tag '${UPDATE_UAS_IMAGE_NAME}:testing' .
	docker rmi '${UPDATE_UAS_IMAGE_NAME}:testing'

chart_setup:
	mkdir -p kubernetes/.packaged
	python3 ./chart_setup.py \
		-v kubernetes/${UPDATE_UAS_CHART_NAME}/values.yaml \
		-c kubernetes/${UPDATE_UAS_CHART_NAME}/Chart.yaml \
		-t ${VERSION}

chart_package: chart_setup
	helm dep up kubernetes/${UPDATE_UAS_CHART_NAME}
	helm package kubernetes/${UPDATE_UAS_CHART_NAME} -d kubernetes/.packaged --app-version ${VERSION} --version ${UPDATE_UAS_CHART_VERSION}

chart_test:
	helm lint "kubernetes/${UPDATE_UAS_CHART_NAME}"
	docker run --rm -v ${PWD}/kubernetes:/apps ${HELM_UNITTEST_IMAGE} -3 ${UPDATE_UAS_CHART_NAME}

clean:
	rm -rf .nox .pytest_cache kubernetes/.packaged
	docker rmi '${UPDATE_UAS_IMAGE_NAME}:${VERSION}' || true
	docker rmi '${UPDATE_UAS_IMAGE_NAME}:testing' || true
