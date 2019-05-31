#!/usr/bin/env bash

yum -y install git iptables-services vim

# Configure iptables so we can fix facter's EC2 checking...
systemctl enable iptables
# If we don't reject all packets to that IP, facter can hang forever, breaking Puppet
iptables -A OUTPUT -j REJECT -d 169.254.169.254
# Make sure the rule comes back when the VM reboots
iptables-save > /etc/sysconfig/iptables

# Add a profile.d file to make sure /usr/local/bin is in the path
cat > /etc/profile.d/local.sh <<LEOF
#!/bin/sh

export PATH="\${PATH}:/usr/local/bin"
LEOF
