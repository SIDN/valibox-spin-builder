#!/bin/sh
IP=`/sbin/get_ip4addr.sh`

if [ "$ACTION" = "ifup" ]; then
        logger "Setting spinweb external address to $IP"
        /sbin/uci set spin.spind.spinweb_interfaces="$IP, 127.0.0.1" &&\ # Obtain current IP address
        /sbin/uci commit

        # Check if SPIN is enabled, restart if so.
        if [ -e /etc/rc.d/S85spinweb ]; then
            /etc/init.d/spinweb restart
        fi
        # We don't have a startup script for autonta
        #  but it does require a restart on interface changes
        /etc/init.d/autonta restart
fi
exit 0
