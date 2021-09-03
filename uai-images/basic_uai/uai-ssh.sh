#!/bin/bash

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

if [ -z "$UAS_PASSWD" ]; then
    echo "UAS_PASSWD not defined"
    exit 1
fi

if [ -z "$UAS_PUBKEY" ]; then
    echo "UAS_PUBKEY not defined"
    exit 1
fi

# Determine port to start sshd on as the user
# Default to 30123 if UAS_NAME is not defined 
if [ -z "$UAS_NAME" ]; then
    UAS_PORT=30123
else
    UAS_PORT=$(printenv $(echo ${UAS_NAME^^}_SERVICE_PORT | tr - _))
    # If this UAI is started with a LoadBalancer service
    # we don't actually want to use 22, instead use 30123
    if [ "$UAS_PORT" -eq 22 ]; then
        UAS_PORT=30123
        if ! [ -z "$LB_TEST_MODE" ]; then
            echo "LOADBALANCER Test: $UAS_PORT"
            exit 1
        fi
    fi
    if [ "$UAS_PORT" -lt 1024 -o "$UAS_PORT" -gt 65535 ]; then
        echo "UAS_PORT:$UAS_PORT is not a valid user port"
        exit 1
    fi
fi

# Collect and set environment variables for the user
UAS_USER=$(echo $UAS_PASSWD | awk -F: '{print $1}')
UAS_UID=$(echo $UAS_PASSWD | awk -F: '{print $3}')
UAS_GID=$(echo $UAS_PASSWD | awk -F: '{print $4}')
UAS_HOME=$(echo $UAS_PASSWD | awk -F: '{print $6}')
echo "Setting up passwd and group entries for ${UAS_USER}"
echo $UAS_PASSWD >> /etc/passwd
echo ":x:$UAS_GID:" >> /etc/group
echo "Setting profile for ${UAS_USER}"
echo "export PS1='[\u@\h \W]\$ '" >> /etc/profile.d/sh.local
echo "if [ -z \$BASH_VERSION ]; then\
 export PS1='[\${USER}@\${HOSTNAME} \${PWD##*/} ]\$ ';\
 fi" >> /etc/profile.d/sh.local
echo "setenv PS1='[\u@\h \W]\$ '" >> /etc/profile.d/csh.local

echo "Adding ${UAS_USER} to groups"
if [ "$UAS_GROUPS" ]; then
    for group in $UAS_GROUPS; do
        usermod -a -G $group $UAS_USER
    done
fi

# Only SSH key-based authentication will be supported by sshd so remove
# the /etc/passwd field for $UAS_USER that triggers /etc/shadow authentication
echo "Disabling password based login"
passwd --delete $UAS_USER

echo "Checking to see if ${UAS_HOME} exists"
echo "If this hangs, please ensure that $UAS_HOME is properly mounted/working on the host of this pod"
# Home directories may not be mounted, create one if needed
if [ ! -d $UAS_HOME ]; then
    echo "No home directory exists, creating one"
    mkdir -p $UAS_HOME;
    chown $UAS_USER $UAS_HOME
fi

# Start munge if installed and a key is found
echo "Checking for munge.key"
MUNGE_KEY=/root/slurm_config/munge/munge.key
if [ -f $MUNGE_KEY -a -x /usr/sbin/munged ]; then
    echo "Setting up munge.key"
    cp $MUNGE_KEY /etc/munge
    chown munge /etc/munge/munge.key
    chmod 0600 /etc/munge/munge.key
    su munge -s /bin/bash -c /usr/sbin/munged
fi

# Copy pbs.conf to the location required by PBS if found
echo "Check for pbs.conf"
if [ -f /etc/pbs/pbs.conf ]; then
    echo "Copying /etc/pbs/pbs.conf to /etc/pbs.conf"
    echo "Remove PBS_PUBLIC_HOST_NAME from /etc/pbs.conf"
    cat /etc/pbs/pbs.conf | grep -v PBS_PUBLIC_HOST_NAME > /etc/pbs.conf
fi

# Initialize ssh and sshd_config
echo "Generating ssh keys and sshd_config"
UAS_SSH=/etc/uas/ssh
mkdir -p $UAS_SSH
/usr/bin/ssh-keygen -A
cat /etc/ssh/sshd_config | egrep -v "^Port|^PrintLastLog|^PrintMotd|^AuthorizedKeysFile|\
                                     ^PasswordAuthentication|^X11UseLocalhost|\
                                     ^X11Forwarding|^ClientAliveInterval|^ClientAliveCountMax" \
                                     > $UAS_SSH/sshd_config
echo "Port $UAS_PORT" >> $UAS_SSH/sshd_config
echo "PrintLastLog no" >> $UAS_SSH/sshd_config
echo "PrintMotd no" >> $UAS_SSH/sshd_config
echo "AuthorizedKeysFile $UAS_SSH/authorized_keys" >> $UAS_SSH/sshd_config
echo "PasswordAuthentication no" >> $UAS_SSH/sshd_config
echo "X11UseLocalhost no" >> $UAS_SSH/sshd_config
echo "X11Forwarding yes" >> $UAS_SSH/sshd_config
# send client keep alives
echo "ClientAliveInterval 120" >> $UAS_SSH/sshd_config
echo "ClientAliveCountMax 720" >> $UAS_SSH/sshd_config
echo "$UAS_PUBKEY" >> $UAS_SSH/authorized_keys
chown $UAS_USER /etc/ssh/ssh_host_* $UAS_SSH/authorized_keys

echo "Checking to see if Cray CLI needs to be initialized"
# Initialize Cray CLI if needed
if [ ! -f $UAS_HOME/.config/cray/configurations/default ]; then
    echo "Creating default cray config"
    su $UAS_USER -c "LANG=en_US.UTF-8 cray init --no-auth --hostname https://api-gw-service-nmn.local"
fi

# Setup macvlan host in /etc/hosts
echo "Checking macvlan settings"
MACVLAN_IP=`ip a show type macvlan | grep nmn1 | grep -oP '(?<=inet\s)\d+(\.\d+){3}'`
if [ ! -z $MACVLAN_IP ]; then
    echo "$MACVLAN_IP `hostname`-nmn" >> /etc/hosts
fi

# Run /sbin/ldconfig to setup modules
echo "Running /sbin/ldconfig -v"
/sbin/ldconfig -v

# List mount points for easier diagnosis when things are missing
# inside the pod
echo "Listing mount points-----"
mount | grep -v -e ^tmpfs -e ^cgroup -e ^proc -e ^overlay -e ^/dev/md126
echo "-------------------------"

# Start sshd as the user
echo "Starting sshd"
su $UAS_USER -c "/usr/sbin/sshd -e -f $UAS_SSH/sshd_config -D"

echo "Not reached - if you see this then sshd failed to start"
