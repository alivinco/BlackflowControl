#!/bin/sh
build_root=/tmp/BlackflyTestSuite
cd ../
rm -r $build_root
mkdir $build_root
cp -r * $build_root
# removed for Jenkins build
#cd ../bf_build
cd /tmp
pwd=$(pwd)
tar -zcvf $pwd/blackfly.tar.gz BlackflyTestSuite/
# tar -zcvf --exclude=.git --exclude=.gitignore --exclude=.idea /tmp/blackfly.tar.gz BlackflyTestSuite/
cp $pwd/blackfly.tar.gz /var/www/blackfly/
cp $build_root/scripts/install.sh /var/www/blackfly