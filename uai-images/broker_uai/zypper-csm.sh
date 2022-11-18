#!/bin/bash
set -e +xv
trap "rm -rf /root/.zypp" EXIT

ARTIFACTORY_USERNAME=$(test -f /run/secrets/ARTIFACTORY_READONLY_USER && cat /run/secrets/ARTIFACTORY_READONLY_USER)
ARTIFACTORY_PASSWORD=$(test -f /run/secrets/ARTIFACTORY_READONLY_TOKEN && cat /run/secrets/ARTIFACTORY_READONLY_TOKEN)
zypper --non-interactive rr --all
zypper addrepo --no-gpgcheck -f https://${ARTIFACTORY_USERNAME}:${ARTIFACTORY_PASSWORD}@artifactory.algol60.net/artifactory/csm-rpms/hpe/stable/sle-15sp2 algol60
zypper --non-interactive source-install cray-switchboard

zypper clean -a && zypper --non-interactive rr --all && rm -f /etc/zypp/repos.d/*
