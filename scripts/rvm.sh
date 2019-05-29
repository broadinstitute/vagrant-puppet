#!/usr/bin/env bash

# Download the installer
wget -O /tmp/install-rvm.sh https://get.rvm.io
bash /tmp/install-rvm.sh

# Cleanup
rm -f /tmp/install-rvm.sh
