{# This script is a mixture of regular bash with the Jinja2 templating language! -#}
#!/bin/bash

# Abort this script on the first failure
set -e

# Add the apt.mopidy.com repository
wget -q -O - https://apt.mopidy.com/mopidy.gpg | apt-key add -
wget -q -O /etc/apt/sources.list.d/mopidy.list https://apt.mopidy.com/buster.list

# Update the software present in the downloaded image
apt update
apt upgrade

# Install Mopidy including all its necessary GStreamer dependencies
apt install mopidy
