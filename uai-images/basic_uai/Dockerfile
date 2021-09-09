# MIT License
#
# (C) Copyright [2020] Hewlett Packard Enterprise Development LP
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

FROM arti.dev.cray.com/baseos-docker-master-local/sles15sp2:latest


ARG SLURM_REPO=http://car.dev.cray.com/artifactory/wlm-slurm/RM/sle15_sp2_cn/x86_64/release/shasta-1.4/
ARG PBS_REPO=http://car.dev.cray.com/artifactory/wlm-pbs/RM/sle15_sp2_cn/x86_64/release/shasta-1.4/

RUN zypper addrepo --no-gpgcheck -f https://artifactory.algol60.net/artifactory/csm-rpms/hpe/stable/ algol60
RUN zypper ref && \
    zypper update -y && \
    zypper install -y curl \
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
RUN zypper install -y --allow-unsigned-rpm cray-uai-util

ENV LC_ALL=C.UTF-8 LANG=C.UTF-8

ENTRYPOINT /usr/bin/uai-ssh.sh
