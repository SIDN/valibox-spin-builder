#!/bin/sh
CHECK_FILE="/etc/bridgemode.on"
if [ -f "$CHECK_FILE" ]; then
    /sbin/ifconfig br-wan  | grep inet6 | head -1 | cut -d ' ' -f 13 | cut -d '/' -f 1
else
    /sbin/ifconfig br-lan  | grep inet6 | head -1 | cut -d ' ' -f 13 | cut -d '/' -f 1
fi
