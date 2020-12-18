#!/bin/sh

# Activate bridge functionality
CHECK_FILE="/etc/bridgemode.on"
COMMAND="$1"

if [ ! -f "/etc/config/firewall.normal" ]; then
    cp /etc/config/firewall /etc/config/firewall.normal
fi
if [ ! -f "/etc/config/network.normal" ]; then
    cp /etc/config/network /etc/config/network.normal
fi

if [ "${COMMAND}" == "on" ]; then
    if [ -f "$CHECK_FILE" ]; then
        echo "checkfile is already set, so it should be on already. Aborting."
        exit 1
    fi
    
    # Turn it on
    # Change configuration files to bridge mode
        cp /etc/config/firewall.bridge /etc/config/firewall &&\
        cp /etc/config/network.bridge /etc/config/network &&\
        /sbin/uci set "wireless.@wifi-iface[0].disabled"='1' &&\
        /sbin/uci commit &&\
        echo "Restarting network" &&\
        /etc/init.d/network restart &&\
        /sbin/fw3 reload &&\
        echo 1 > "$CHECK_FILE" &&\
        exit 0
elif [ "${COMMAND}" == "off" ]; then
    if [ ! -f "$CHECK_FILE" ]; then
        echo "Checkfile does not exist, nothing to turn off. Aborting"
        exit 1
    fi
    cp /etc/config/firewall.normal /etc/config/firewall &&\
        cp /etc/config/network.normal /etc/config/network &&\
        /sbin/uci set "wireless.@wifi-iface[0].disabled"='0' &&\
        /sbin/uci commit &&\
        echo "Restarting network" &&\
        /etc/init.d/network restart &&\
        /sbin/fw3 reload &&\
        rm "$CHECK_FILE" &&\
        exit 0
else
    # Check status, return 0 when in bridge mode, -1 otherwise.
    if [ -f "$CHECK_FILE" ]; then
        exit 0
    fi
    exit 10
fi
# TODO change uci spin.spind.spinweb_interface...
