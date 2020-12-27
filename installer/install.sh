{# This script is a mixture of regular bash with the Jinja2 templating language! -#}
{# It is automatically split at each reboot command and a restart procedure after #}
{# the reboot is added. This also adds the shebang - there is no need for one here#}

{% if cookiecutter.hostname != 42|hostname %}
# Set the given hostname
echo {{ cookiecutter.hostname }} > /etc/hostname
sed -i "s/127.0.1.1.*{{ 42|hostname }}/127.0.1.1\t{{ cookiecutter.hostname}}/g" /etc/hosts
{% endif %}

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

# Copy the configuration
cp ./installer/mopidy.conf ~/.config/mopidy
