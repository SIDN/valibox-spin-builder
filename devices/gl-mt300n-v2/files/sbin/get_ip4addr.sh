#!/bin/sh

NOTHING=$(/sbin/bridge.sh)
STATUS=$?
# STATUS is 0 (default) or 1 (bridge mode), or anything <0 otherwise

if [ "$STATUS" == 1 ]; then
    /sbin/ifconfig br-wan  | grep inet | head -1 | cut -d ' ' -f 12 | cut -d ':' -f 2
else
    /sbin/ifconfig br-lan  | grep inet | head -1 | cut -d ' ' -f 12 | cut -d ':' -f 2
fi
