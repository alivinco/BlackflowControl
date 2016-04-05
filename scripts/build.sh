#!/bin/sh
build_root=/tmp/BlackflowControl
cd ../
rm -r $build_root
mkdir $build_root
cp -r * $build_root
# removed for Jenkins build
#cd ../bf_build
cd /tmp
pwd=$(pwd)
tar -zcvf $pwd/bfctrl.tar.gz BlackflowControl/
# tar -zcvf --exclude=.git --exclude=.gitignore --exclude=.idea /tmp/blackfly.tar.gz BlackflyTestSuite/
cp $pwd/blackfly.tar.gz /var/www/bfctrl/
cp $build_root/scripts/install.sh /var/www/bfctrl
cp $build_root/scripts/install_debian.sh /var/www/bfctrl