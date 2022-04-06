#!/bin/bash
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
# A simple function to unconditionally restart a command if it exits.
# This was implemented instead of enabling systemd in a container for sssd.
# In certain scenarios, sssd may exit (connectivity issues) and the broker
# could require sssd for new connections.
# Callers should make sure the process runs in the foreground and the function
# itself must be backgrounded for the rest of the script to proceed.
function process_watcher() {

    if [ -z $1 ]; then
        echo "process_watcher: No command was specified."
        exit 1
    fi

    while true; do
        $1
        echo "process_watcher: "$1" exited with exit code $?. Restarting..."
        sleep 3
    done
}

echo "Configure PAM to use sssd..."
pam-config -a --sss --mkhomedir

echo "Generating broker host keys..."
# If the installed version of switchboard supports shared keys for replicas,
# generate the key that way.  If that fails, fall back to a local host key.
/usr/bin/switchboard hostkey || ssh-keygen -A

echo "Checking for UAI_CREATION_CLASS..."
if ! [ -z $UAI_CREATION_CLASS ]; then
    echo UAI_CREATION_CLASS=$UAI_CREATION_CLASS >> /etc/environment
    echo UAI_SHARED_SECRET_PATH=$UAI_SHARED_SECRET_PATH >> /etc/environment
    echo UAI_REPLICAS=$UAI_REPLICAS >> /etc/environment
fi

echo "Starting sssd..."
process_watcher "sssd -i" &

echo "Starting sshd..."
/usr/sbin/sshd -f /etc/switchboard/sshd_config -D
