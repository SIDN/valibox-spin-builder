#!/bin/sh
CHECK_FILE="/etc/bridgemode.on"
if [ -f "$CHECK_FILE" ]; then
    /sbin/ifconfig br-wan  | grep inet | head -1 | cut -d ' ' -f 12 | cut -d ':' -f 2
else
    /sbin/ifconfig br-lan  | grep inet | head -1 | cut -d ' ' -f 12 | cut -d ':' -f 2
fi
