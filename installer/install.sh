{# This script is a mixture of regular bash with the Jinja2 templating language! -#}
{# It is automatically split at each reboot command and a restart procedure after #}
{# the reboot is added. This also adds the shebang - there is no need for one here#}

{# TODO: Check for the pi/raspberry password combination and force the user to change #}
{# https://stackoverflow.com/questions/18035093/given-a-linux-username-and-a-password-how-can-i-test-if-it-is-a-valid-account/18035305 #}

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

# Install Mopidy extensions and their dependencies
{% if cookiecutter.youtube == "Yes" %}
apt install gstreamer1.0-plugins-bad
python3 -m pip install https://github.com/natumbri/mopidy-youtube/archive/develop.zip
{% endif %}

{% if cookiecutter.device == "rc522" %}
# Enable SPI
sed -i 's/#dtparam=spi=on/dtparam=spi=on/g' /boot/config.txt
{% endif %}

{% if cookiecutter.power_switch == "Simple" %}
# Configure the GPIO driven shutdown/wake up for the button
echo "[all]" >> /boot/config.txt
echo "dtoverlay=gpio-shutdown,active_low=0" >>  /boot/config.txt

# Move the Python script that performs shutdown upon boot by power cord
cp ./installer/gpio_if.sh /usr/local/sbin

# Add the systemd service that syncs the switch with the Pi state after a boot that was
# triggered by inserting the power cord.
cp ./installer/powerswitch-sync.service /etc/systemd/system
{% endif %}

{% if cookiecutter.development_setup == "Yes" %}
{% endif %}

# Install the Vyvo Python package and the Mopidy configuration
{% if cookiecutter.production == "Yes" %}
# Globally install extensions+configuration and activate systemd service
python3 -m pip install git+https://github.com/dokempf/vyvo-player.git
cp ./installer/mopidy.conf /etc/mopidy
usermod -a -G spi mopidy
usermod -a -G gpio mopidy
systemctl enable mopidy
{% else %}
# Install editable from git main branch and use local configuration
git clone https://github.com/dokempf/vyvo-player.git
python3 -m pip install -e vyvo-player
cp ./installer/mopidy.conf ~/.config/mopidy

# Install some development tools that I typically enjpy having around
python3 -m pip install IPython pudb
{% endif %}

#TODO: Show WIRING.md here

# Plenty of changes above require a reboot
reboot

{% if cookiecutter.power_switch == "Simple" %}
# If we enable this service before the button is properly connected, the
# Pi will shutdown on all start-ups, which will be a proper nightmare for
# users. We therefor only enable it, if the button is in place.
/usr/local/sbin/gpio_if.sh 2 1 echo "WARNING: Your power switch seems to be wired wrongly. Manually run 'sudo systemctl enable powerswitch-sync' after fixing."
/usr/local/sbin/gpio_if.sh 2 0 systemctl enable powerswitch-sync
{% endif %}
