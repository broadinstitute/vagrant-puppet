#!/usr/bin/env bash

rpm --import https://yum.puppet.com/RPM-GPG-KEY-puppet
rpm --import https://yum.puppet.com/RPM-GPG-KEY-puppetlabs
yum -y install https://yum.puppet.com/puppet5-release-el-7.noarch.rpm
yum -y install pdk

mkdir -p /etc/puppetlabs/code/hieradata
mkdir -p /etc/puppetlabs/code/modules
echo '---' > /etc/puppetlabs/code/hieradata/global.yaml

# Write the hiera.yaml file
cat > /etc/puppetlabs/code/hiera.yaml <<PEOF
---
version: 5
defaults:
  datadir: /etc/puppetlabs/code/hieradata
  data_hash: yaml_data
hierarchy:
  - name: 'Global'
    path: 'global.yaml'
PEOF
