# MIT License
#
# (C) Copyright [2022] Hewlett Packard Enterprise Development LP
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

FROM artifactory.algol60.net/csm-docker/stable/docker.io/library/alpine:3 as base
WORKDIR /test
RUN mkdir -p /test

RUN apk add --upgrade --no-cache apk-tools && \
    apk update && \
    apk add --no-cache py3-pip python3-dev && \
    apk add --no-cache curl && \
    apk add --no-cache vim && \
    apk add --no-cache openssh && \
    apk add --no-cache which && \
    apk -U upgrade --no-cache

ENV VIRTUAL_ENV=/test/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN pip install requests
RUN pip install pyyaml 
RUN pip3 install --upgrade pip

# Run unit tests
FROM base as testing

# Build Application Image
FROM base as app 

WORKDIR /test
RUN mkdir -p /test
RUN chmod 755 /test
RUN mkdir -p /root/.ssh
RUN chmod 0700 /root/.ssh

RUN echo -e "PasswordAuthentication no" >> /etc/ssh/sshd_config
RUN echo -e "Port 30123" >> /etc/ssh/sshd_config
RUN ssh-keygen -A

COPY ./test/gateway-test.py /test/gateway-test.py
COPY ./test/gateway-test-defn.yaml /test/gateway-test-defn.yaml
COPY ./test/entrypoint.sh /test/entrypoint.sh
RUN chmod 755 /test/entrypoint.sh
COPY ./test/run-test.sh /test/run-test.sh
RUN chmod 755 /test/run-test.sh

ENTRYPOINT ["/test/entrypoint.sh"]
