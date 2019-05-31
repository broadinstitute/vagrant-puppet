#!/usr/bin/env bash

export PUPPET_GEM_VERSION='< 6.0.0'

# shellcheck source=/dev/null
source /etc/profile.d/rvm.sh

# For some reason the checksums don't match, so skip (I know...bad security...)
rvm install 2.4.2 --verify-downloads 2

gem install bundle librarian-puppet rake --no-rdoc --no-ri
bundle config --global silence_root_warning 1
