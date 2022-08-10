#!/bin/bash
set -e +xv
trap "rm -rf /root/.zypp" EXIT

source /run/secrets/sles
zypper --non-interactive rr --all
zypper addrepo --no-gpgcheck -f https://${ARTIFACTORY_USERNAME}:${ARTIFACTORY_PASSWORD}@artifactory.algol60.net/artifactory/csm-rpms/hpe/stable/sle-15sp2 algol60
zypper --non-interactive source-install cray-switchboard

zypper clean -a && zypper --non-interactive rr --all && rm -f /etc/zypp/repos.d/*
