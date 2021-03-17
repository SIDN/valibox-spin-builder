#!/bin/sh

# Runs on startup.
# Makes sure physical switch setting is honored.

# BTN_8 is either hi (bridge) or lo (default)
NOTHING=$(/sbin/bridge.sh)
STATUS=$?
# STATUS is 0 (default) or 1 (bridge mode), or anything <0 otherwise

if [ "${STATUS}" == "0" ]; then
    COMMAND="off"
elif [ "${STATUS}" == "1" ]; then
    COMMAND="on"
else
    logger "Bridge-mode startup error: ${STATUS}"
    exit -1
fi

# Make LED blink while setting up
echo "timer" > /sys/class/leds/gl-ar150\:orange\:wlan/trigger
/sbin/bridge.sh "${COMMAND}"
if [ $? -eq 0 ]; then
    echo "none" > /sys/class/leds/gl-ar150\:orange\:wlan/trigger
    echo 1 > /sys/class/leds/gl-ar150\:orange\:wlan/brightness
fi
