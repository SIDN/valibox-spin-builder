#!/bin/sh

/sbin/ifconfig -a | grep HWaddr | tail -1 | sed 's/^.*\(.\).\(.\)\(.\)..$/\1\2\3/' | awk '{print tolower($0)}'
