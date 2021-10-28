#! /bin/bash

# Temporary entry point so I can do some prototyping in an interactive
# UAI with K8s access.
env | grep KUBERNETES | sed -e 's/^/export /' > /etc/profile.d/k8s_env.sh

exec /usr/bin/uai-ssh.sh
