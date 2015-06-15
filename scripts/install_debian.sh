#!/bin/sh
cd /tmp
curl -O http://lego.fiicha.net/blackfly/blackfly.tar.gz
rm -r BlackflyTestSuite
tar -zxvf blackfly.tar.gz
cd BlackflyTestSuite/
chmod a+x setup_debian.sh
sudo ./setup_debian.sh
