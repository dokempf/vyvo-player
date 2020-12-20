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

{% if cookiecutter.device == "rc522" %}
# Enable SPI
sed -i 's/#dtparam=spi=on/dtparam=spi=on/g' /boot/config.txt
{% endif %}

{% if cookiecutter.development_setup == "Yes" %}
# Install some development tools that I typically enjpy having around
python3 -m pip install IPython pudb
{% endif %}

# Install the Vyvo Python package
{% if cookiecutter.development_setup == "Yes" %}
git clone https://github.com/dokempf/vyvo-player.git
python3 -m pip install -e vyvo-player
{% else %}
python3 -m pip install git+https://github.com/dokempf/vyvo-player.git
{% endif %}
