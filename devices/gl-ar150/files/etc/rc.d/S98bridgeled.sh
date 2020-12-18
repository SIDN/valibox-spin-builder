#!/bin/sh

CHECK_FILE="/etc/bridgemode.on"

if [ -f "$CHECK_FILE" ]; then
    echo 1 > /sys/class/leds/gl-ar150\:orange\:wlan/brightness
else
    echo 0 > /sys/class/leds/gl-ar150\:orange\:wlan/brightness
fi
