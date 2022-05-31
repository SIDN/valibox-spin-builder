#!/bin/sh

CHECK_FILE="/etc/first_run.done"

if [ -f "$CHECK_FILE" ]; then
    echo "first run already done, delete $CHECK_FILE to run setup again"
else
    sleep 5
    # generate unbound_control key and cert
    /usr/sbin/unbound-control-setup

    # just in case we are slow, wait for a link-local address on br-lan
    echo "doing first run setup"
    HWADDR=`/sbin/get_hwaddr.sh`
    # If we want to automatically determine ip addresses we could use
    # this, but currently they are hard-configured to local address
    # space anyway
    #IP4ADDR=`/sbin/get_ip4addr.sh`
    #IP6ADDR=`/sbin/get_ip6addr.sh`
    
    # Replace addresses in unbound.conf file
    #cat /etc/unbound/unbound.conf.in | sed "s/XIP4ADDRX/${IP4ADDR}/" | sed "s/XIP6ADDRX/${IP6ADDR}/" > /etc/unbound/unbound.conf
    cp /etc/unbound/unbound.conf.in /etc/unbound/unbound.conf
    
    cat /etc/config/wireless.in | sed "s/XHWADDRX/${HWADDR}/" > /etc/config/wireless

    # Replace dnsmasq conf
    cp /etc/config/dhcp.in /etc/config/dhcp

    # Store results
    touch "$CHECK_FILE"
    #echo "LAN IPv4: ${IP4ADDR}" >> "$CHECK_FILE"
    #echo "LAN IPv6: ${IP6ADDR}" >> "$CHECK_FILE"
    echo "SSID:     SIDN-GL-Inet-${HWADDR}" >> "$CHECK_FILE"
    /etc/init.d/network restart
    
    # Show the current version in the main html menu
    VERSION=`cat /etc/valibox.version`
    cat /www/index.html.in | sed "s/XVERSIONX/${VERSION}/" > /www/index.html
    
    # sleep some more
    sleep 5
    # we run before dnsmasq and unbound so restarting those is not necessare
fi
