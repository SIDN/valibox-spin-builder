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
    # Turn to bridge mode
    # Change configuration files to bridge mode
    ln -f -s /etc/config/firewall.bridge /etc/config/firewall &&\
    ln -f -s /etc/config/network.bridge /etc/config/network &&\
    /sbin/uci set "wireless.@wifi-iface[0].disabled"='1' &&\
    /sbin/uci commit &&\
    echo "Restarting network" &&\
    /etc/init.d/network restart &&\
    /sbin/fw3 reload &&\
    /sbin/uci set spin.spind.spinweb_interfaces="`/sbin/get_ip4addr.sh`, 127.0.0.1" &&\ # Obtain current IP address
    /sbin/uci commit &&\
    /etc/init.d/spinweb restart &&\
    exit 0
elif [ "${COMMAND}" == "off" ]; then
    # Turn to default (nat) mode
    ln -f -s /etc/config/firewall.normal /etc/config/firewall &&\
    ln -f -s /etc/config/network.normal /etc/config/network &&\
    /sbin/uci set "wireless.@wifi-iface[0].disabled"='0' &&\
    /sbin/uci commit &&\
    echo "Restarting network" &&\
    /etc/init.d/network restart &&\
    /sbin/fw3 reload &&\
    /sbin/uci set spin.spind.spinweb_interfaces="`/sbin/get_ip4addr.sh`, 127.0.0.1" &&\ # Obtain current IP address
    /sbin/uci commit &&\
    /etc/init.d/spinweb restart &&\
    exit 0
else
    # Check status, return 0 when in bridge mode, 1 otherwise.
    NOTHING=$(cat /sys/kernel/debug/gpio | grep BTN_8 | grep lo)
    STATUS=$?
    # STATUS is 0 (default) or 1 (bridge mode)
    exit $STATUS
fi
