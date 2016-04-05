#!/bin/sh
cd /tmp
curl -O http://lego.fiicha.net/zmarlin/bfctrl.tar.gz
rm -r BlackflowControl
tar -zxvf blackfly.tar.gz
cd BlackflowControl/
chmod a+x setup_debian.sh
sudo ./setup_debian.sh
