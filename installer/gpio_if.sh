#!/bin/bash

# Arguments:
# $1: The GPIO Pin to use
# $2: The value (0, 1) to trigger for
# $3: The command to execute

echo "$1" > /sys/class/gpio/export
echo "in" > /sys/class/gpio/gpio$1/direction

STATE=`cat /sys/class/gpio/gpio$1/value`

if [ "x$STATE" = "x$2" ]; then
    "$3"
fi

echo "$1" > /sys/class/gpio/unexport
