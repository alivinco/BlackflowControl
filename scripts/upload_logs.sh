#!/bin/sh
# touch /media/app/upload_logs.sh;chmod a+x /media/app/upload_logs.sh
mkdir -p /tmp/ssh
chmod 0700 /tmp/ssh
touch /tmp/ssh/tunneluser
chmod 0600 /tmp/ssh/tunneluser
echo "-----BEGIN RSA PRIVATE KEY----- MIIEoQIBAAKCAQEAuuW24...Q== -----END RSA PRIVATE KEY-----" > /tmp/ssh/tunneluser
gw_serial=$(grep -Po '^Serial\s*:\s*\K[[:xdigit:]]{16}' /proc/cpuinfo)
date=$(date +%F_%H.%M.%S)
f_name="/tmp/cpu_serial_${gw_serial}_${date}.tar.gz"
echo $f_name
tar -zcvf $f_name /var/log/z-wave-drv.log /var/log/cwmp/zwta.log /media/app/zwave/zwcfg*.xml
scp -P 443 -i /tmp/ssh/tunneluser $f_name reverse@lego.fiicha.net:/var/www/logs/smartly/
