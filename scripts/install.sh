#!/bin/sh
cd /tmp
curl -O http://lego.fiicha.net/bfctrl/bfctrl.tar.gz
rm -r BlackflowControl
tar -zxvf bfctrl.tar.gz
cd BlackflowControl/
chmod a+x setup_sg.sh
sudo ./setup_sg.sh
