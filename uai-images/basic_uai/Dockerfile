#
# MIT License
#
# (C) Copyright 2020-2022 Hewlett Packard Enterprise Development LP
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
FROM artifactory.algol60.net/csm-docker/stable/registry.suse.com/suse/sle15:15.3 as base

ARG SLES_REPO_USERNAME
ARG SLES_REPO_PASSWORD
ARG SLES_MIRROR="https://${SLES_REPO_USERNAME}:${SLES_REPO_PASSWORD}@artifactory.algol60.net/artifactory/sles-mirror"
ARG SLES_VERSION=15-SP3
ARG ARCH=x86_64
RUN \
  zypper --non-interactive rr --all && \
  zypper --non-interactive ar ${SLES_MIRROR}/Products/SLE-Module-Basesystem/${SLES_VERSION}/${ARCH}/product?auth=basic sles15sp3-Module-Basesystem-product && \
  zypper --non-interactive ar ${SLES_MIRROR}/Updates/SLE-Module-Basesystem/${SLES_VERSION}/${ARCH}/update?auth=basic sles15sp3-Module-Basesystem-update && \
  zypper update -y && \
  zypper install -y awk \
                    curl \
                    glibc-locale-base \
                    gzip \
                    iputils \
                    jq \
                    less \
                    openssh \
                    rsync \
                    tar \
                    vim \
                    wget \
                    which

RUN zypper addrepo --no-gpgcheck -f https://artifactory.algol60.net/artifactory/csm-rpms/hpe/stable/sle-15sp2 algol60 && \
    zypper install -y --allow-unsigned-rpm cray-uai-util
 
RUN zypper clean -a && zypper --non-interactive rr --all && rm -f /etc/zypp/repos.d/* && rm -Rf /root/.zypp

ENV LC_ALL=C.UTF-8 LANG=C.UTF-8

ENTRYPOINT /usr/bin/uai-ssh.sh
