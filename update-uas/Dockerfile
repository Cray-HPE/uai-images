# MIT License
#
# (C) Copyright [2021] Hewlett Packard Enterprise Development LP
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
FROM alpine:3.14.0 as base

run apk update && apk add python3 py3-pip
run apk upgrade

RUN pip3 install --upgrade pip
RUN mkdir -p /app/src
COPY requirements.txt /app
COPY src/update_uas.py /app/src/update_uas.py
RUN pip3 install --no-cache-dir \
                 --index-url http://dst.us.cray.com/dstpiprepo/simple \
                 --trusted-host dst.us.cray.com -r /app/requirements.txt

# Run unit tests
FROM base as testing
COPY src/test_update_uas.py /app/src/test_update_uas.py
COPY noxfile.py .coveragerc requirements-lint.txt requirements-style.txt requirements-test.txt /app/
RUN pip3 install nox
RUN pip3 install --no-cache-dir -r /app/requirements-lint.txt
RUN pip3 install --no-cache-dir -r /app/requirements-style.txt
RUN pip3 install --no-cache-dir -r /app/requirements-test.txt
ARG FORCE_TESTS=null
RUN cd /app && NOX_DOCKER_BUILD=yes nox
ENTRYPOINT ["/bin/sh", "-ce", "cd /app && NOX_DOCKER_BUILD=yes nox"]

# Create the actual job layer that will, ultimately, run update_uas.py.
# the entrypoint here is a stub because the real entrypoint will be set
# by the Helm chart based on the image list / versions.
FROM base as app
ENTRYPOINT ["/bin/echo", "Override this entrypoint to run application"]
