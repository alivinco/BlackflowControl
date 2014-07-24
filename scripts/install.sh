#!/bin/sh
curl -O http://lego.fiicha.net/blackfly/blackfly.tar.gz
rm -r BlackflyTestSuite
tar -zxvf blackfly.tar.gz
cd BlackflyTestSuite/
chmod a+x setup_sg.sh
./setup_sg.sh
