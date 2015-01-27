#!/bin/sh
gw_serial=$(grep -Po '^Serial\s*:\s*\K[[:xdigit:]]{16}' /proc/cpuinfo)
date=$(date +%F_%H.%M.%S)
f_name="/tmp/cpu_serial_${gw_serial}_${date}.tar.gz"
echo $f_name
tar -zcvf $f_name /var/log/z-wave-drv.log /var/log/cwmp/zwta.log /media/app/zwave/zwcfg*.xml
scp -P 443 -i /tmp/ssh/tunneluser $f_name reverse@lego.fiicha.net:/var/www/logs/smartly/
