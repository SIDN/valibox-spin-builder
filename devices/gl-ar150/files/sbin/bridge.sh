#!/bin/sh

# Activate bridge functionality
COMMAND="$1"

# If the architecture does not support bridge-modes, /etc/config/firewall and network are not a symlink
# Then, we quit indicating default mode, there is nothing to possibly do.
if [[ $(readlink -f /etc/config/firewall) == "/etc/config/firewall" && $(readlink -f /etc/config/network) == "/etc/config/network" ]]; then
    exit 0
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
    exit 1
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
