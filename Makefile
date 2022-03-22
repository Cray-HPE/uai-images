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

NAME ?= cray-uai-images
UPDATE_UAS_DIR ?= update-uas
BASIC_UAI_DIR ?= uai-images/basic_uai
BROKER_UAI_DIR ?= uai-images/broker_uai
GATEWAY_TEST_UAI_DIR ?= uai-images/gateway_test_uai
VERSION ?= $(shell cat .version)

all: chart docker

chart:  chart_test chart_package
docker: docker_basic_uai docker_broker_uai docker_gateway_test_uai docker_update_uas
chart_package: chart_package_update_uas
unit_test: chart_test unit_test_update_uas
chart_test: chart_test_update_uas
clean: clean_basic_uai clean_broker_uai clean_gateway_test_uai clean_update_uas

docker_basic_uai:
	(cd ${BASIC_UAI_DIR}; make docker)

clean_basic_uai:
	(cd ${BASIC_UAI_DIR}; make clean)

docker_broker_uai:
	(cd ${BROKER_UAI_DIR}; make docker)

clean_broker_uai:
	(cd ${BROKER_UAI_DIR}; make clean)

docker_gateway_test_uai:
	(cd ${GATEWAY_TEST_UAI_DIR}; make docker)

clean_gateway_test_uai:
	(cd ${GATEWAY_TEST_UAI_DIR}; make clean)

docker_update_uas:
	(cd ${UPDATE_UAS_DIR}; make docker)

unit_test_update_uas:
	(cd ${UPDATE_UAS_DIR}; make unit_test)

chart_package_update_uas:
	(cd ${UPDATE_UAS_DIR}; make chart_package)

chart_test_update_uas:
	(cd ${UPDATE_UAS_DIR}; make chart_test)

clean_update_uas:
	(cd ${UPDATE_UAS_DIR}; make clean)
