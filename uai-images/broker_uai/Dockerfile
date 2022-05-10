# MIT License
#
# (C) Copyright [2020-2022] Hewlett Packard Enterprise Development LP
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
  zypper --non-interactive ar ${SLES_MIRROR}/Products/SLE-Module-Development-Tools/${SLES_VERSION}/${ARCH}/product?auth=basic sles15sp3-Module-Development-Tools-product && \
  zypper --non-interactive ar ${SLES_MIRROR}/Updates/SLE-Module-Development-Tools/${SLES_VERSION}/${ARCH}/update?auth=basic sles15sp3-Module-Development-Tools-update && \
  zypper update -y

RUN zypper addrepo --no-gpgcheck -f https://artifactory.algol60.net/artifactory/csm-rpms/hpe/stable/sle-15sp2 algol60

WORKDIR /app

FROM base as build 

RUN zypper install -y go tar bzip2
RUN zypper --non-interactive source-install cray-switchboard
RUN ( \
     cd /usr/src/packages/SOURCES && \
     bunzip2 cray-switchboard-*.tar.bz2 && \
     tar xf cray-switchboard-*.tar && \
     mkdir /app/switchboard && \
     cp -r cray-switchboard-*/* /app/switchboard \
    )
RUN ( \
     cd /app/switchboard && \
     export GO111MODULE=on && \
     go get && \
     go build -o switchboard main.go \
    )

# Install switchboard

FROM base as application

# Install packages used by the entrypoint script
RUN zypper install -y openssh \
                      sssd \
                      vim \
                      jq \
                      curl

RUN zypper clean -a && zypper --non-interactive rr --all && rm -f /etc/zypp/repos.d/* && rm -Rf /root/.zypp

# Bring in the broker entrypoint and some config
COPY ./broker/nsswitch.conf /etc/nsswitch.conf
COPY ./broker/entrypoint.sh /app/broker/entrypoint.sh

# Copy switchboard binary and configs from the build layer
COPY --from=build /app/switchboard/src/sshd_config /etc/switchboard/sshd_config
COPY --from=build /app/switchboard/switchboard /usr/bin/switchboard

# Create directories for sssd
RUN mkdir -p /var/lib/sss/db \
             /var/lib/sss/keytabs \
             /var/lib/sss/mc \
             /var/lib/sss/pipes \
             /var/lib/sss/pipes/private \
             /var/lib/sss/pubconf

# Set the locale for craycli
ENV LC_ALL=C.UTF-8 LANG=C.UTF-8

ENTRYPOINT ["/app/broker/entrypoint.sh"]
