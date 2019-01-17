#!/bin/sh

# For VirtualBox, the resulting image needs a bit of tweaking...
cp bin/target/x86/64/openwrt-x86_64-combined-squashfs.img.gz /tmp
cd /tmp
gunzip openwrt-x86-64-combined-squashfs.img.gz 
dd if=openwrt-x86-64-combined-squashfs.img of=openwrt.img bs=128000 conv=sync
VBoxManage convertfromraw --format VDI openwrt.img openwrt-x86-64-combined-squashfs.vdi
# cp to result? back to bin/target?


#if already done earlier, the vdi must be removed:
#rm openwrt-x86-64-combined-squashfs.vdi 


#Other notes:
#- virtual machine needs two network cards (do details matter? apart from LAN and bridge mode)
#- virtual machine needs >64mb memory (for enough room to upgrade from .img)
#- upgrade can be done with the gunzipped .img
#
#'board name' needs separate mention per type, i fear...

