#!/bin/sh
build_root=/tmp/BlackflyTestSuite
cd ../
rm -r $build_root
mkdir $build_root
cp -r * $build_root
cd ../bf_build
pwd=$(pwd)
cd /tmp
tar -zcvf $pwd/blackfly.tar.gz BlackflyTestSuite/
cp $pwd/blackfly.tar.gz /var/www/blackfly/
cp $build_root/scripts/install.sh /var/www/blackfly