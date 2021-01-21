#!/bin/sh
IP=`/sbin/get_ip4addr.sh`

if [ "$ACTION" = "ifup" ]; then
        logger "Setting spinweb external address to $IP"
        /sbin/uci set spin.spind.spinweb_interfaces="$IP, 127.0.0.1" &&\ # Obtain current IP address
        /sbin/uci commit &&\
        /etc/init.d/spinweb restart
fi
exit 0