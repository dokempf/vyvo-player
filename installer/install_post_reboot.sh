#!/bin/bash

set -e

# Remove this script invocation from bashrc
sed -i "s|sudo ./installer/install_post_reboot.sh||g" ~/.bashrc

{% if cookiecutter.power_switch == "Simple" %}
# If we enable this service before the button is properly connected, the
# Pi will shutdown on all start-ups, which will be a proper nightmare for
# users. We therefor only enable it, if the button is in place.
/usr/local/sbin/gpio_if.sh 2 1 echo "WARNING: Your power switch seems to be wired wrongly. Manually run 'sudo systemctl enable powerswitch-sync' after fixing."
/usr/local/sbin/gpio_if.sh 2 0 systemctl enable powerswitch-sync
{% endif %}
