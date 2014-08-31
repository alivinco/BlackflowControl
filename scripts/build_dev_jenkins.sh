#!/bin/sh
build_root=/tmp/BlackflyTestSuite
publish_root=/var/www/blackfly/develop
rm -r $build_root
mkdir $build_root
cp -r * $build_root
cd /tmp
pwd=$(pwd)
tar -zcvf $pwd/blackfly.tar.gz BlackflyTestSuite/
cp $pwd/blackfly.tar.gz $publish_root
cp $build_root/scripts/install.sh $publish_root
cp $build_root/scripts/install_debian.sh $publish_root
echo "Build Id:${BUILD_ID} Git commit:${GIT_COMMIT} " > $publish_root/build_info.txt
sed -i -e  "s|/blackfly/blackfly.tar.gz|/blackfly/develop/blackfly.tar.gz|g" $publish_root/install.sh
sed -i -e  "s|/blackfly/blackfly.tar.gz|/blackfly/develop/blackfly.tar.gz|g" $publish_root/install_debian.sh