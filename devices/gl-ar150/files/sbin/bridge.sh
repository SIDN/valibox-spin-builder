#!/bin/sh

# SPIN check file to see if bridge mode is active
CHECK_FILE="/etc/bridge.active"

# Activate bridge functionality
COMMAND="$1"

# If the architecture does not support bridge-modes, /etc/config/firewall and network are not a symlink
# Then, we quit indicating default mode, there is nothing to possibly do.
if [[ $(readlink -f /etc/config/firewall) == "/etc/config/firewall" && $(readlink -f /etc/config/network) == "/etc/config/network" ]]; then
    exit 0
fi

if [ "${COMMAND}" == "on" ]; then
    # Check if turning on is needed
    if [ -e "$CHECK_FILE" ]; then
        # Nothing to do, bridge mode is already active
        exit 1
    fi

    # Turn to bridge mode
    # Change configuration files to bridge mode
    ln -f -s /etc/config/firewall.bridge /etc/config/firewall &&\
    ln -f -s /etc/config/network.bridge /etc/config/network &&\
    /sbin/uci set "wireless.@wifi-iface[0].disabled"='1' &&\
    /sbin/uci commit &&\
    echo 1 > "$CHECK_FILE"

    # Reboot to make sure everything gets set correctly
    sleep 2
    reboot
    exit 1
elif [ "${COMMAND}" == "off" ]; then
    # Check if turning on is needed
    if [ ! -e "$CHECK_FILE" ]; then
        # Nothing to do, default nat mode is active
        exit 0
    fi

    # Turn to default (nat, router) mode
    ln -f -s /etc/config/firewall.router /etc/config/firewall &&\
    ln -f -s /etc/config/network.router /etc/config/network &&\
    /sbin/uci set "wireless.@wifi-iface[0].disabled"='0' &&\
    /sbin/uci commit &&\
    rm -f "$CHECK_FILE"

    # Reboot to make sure everything gets set correctly
    sleep 2
    reboot
    exit 0
else
    # Check status, return 0 when in bridge mode, 1 otherwise.
    # In openwrt<=19.07
    #NOTHING=$(cat /sys/kernel/debug/gpio | grep BTN_8 | grep hi)
    # In openwrt>=21.2
    NOTHING=$(cat /sys/kernel/debug/gpio | grep gpio-7 | grep hi)
    STATUS=$?
    # STATUS is 0 (default) or 1 (bridge mode or error)
    exit $STATUS
fi
