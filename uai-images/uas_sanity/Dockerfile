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

FROM arti.dev.cray.com/baseos-docker-master-local/sles15sp2:latest as base

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
                      python3 \
                      rsync \
                      tar \
                      vim \
                      wget \
                      which && \
    zypper install -y emacs   # ERIC TAKE THIS OUT WHEN YOU HAVE WORKING CODE
RUN zypper install -y --allow-unsigned-rpm cray-uai-util
RUN pip install requests kubernetes
RUN pip3 install --upgrade pip
RUN mkdir -p /app/src
COPY requirements.txt /app
COPY src/uas_sanity_test.py /app/src/uas_sanity_test.py
RUN pip3 install --no-cache-dir -r /app/requirements.txt

# Run unit tests
FROM base as testing
COPY src/test_uas_sanity_test.py /app/src/src/test_uas_sanity_test.py
COPY pylintrc noxfile.py .coveragerc requirements-lint.txt requirements-style.txt requirements-test.txt /app/
RUN pip3 install nox
RUN pip3 install --no-cache-dir -r /app/requirements-lint.txt
RUN pip3 install --no-cache-dir -r /app/requirements-style.txt
RUN pip3 install --no-cache-dir -r /app/requirements-test.txt
ARG FORCE_TESTS=null
RUN cd /app && NOX_DOCKER_BUILD=yes nox
ENTRYPOINT ["/bin/sh", "-ce", "cd /app && NOX_DOCKER_BUILD=yes nox"]

FROM base as app
ENV LC_ALL=C.UTF-8 LANG=C.UTF-8
ENTRYPOINT /usr/bin/uai-ssh.sh  # ERIC CHANGE THIS TO RUN THE TEST WHEN THE TIME COMES
