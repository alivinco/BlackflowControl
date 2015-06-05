#!/bin/sh
build_root=/tmp/BlackflyTestSuite
publish_root=/var/www/blackfly/develop
echo "{\"build_id\":\"${BUILD_ID}\",\"git_commit\":\"${GIT_COMMIT}\",\"git_branch\":\"develop\"}" > configs/build_info.json
rm -r $build_root
mkdir $build_root
cp -r * $build_root
cd /tmp
pwd=$(pwd)
tar -zcvf $pwd/blackfly.tar.gz BlackflyTestSuite/
cp $pwd/blackfly.tar.gz $publish_root
cp $build_root/scripts/install.sh $publish_root
cp $build_root/scripts/install_debian.sh $publish_root
cp $build_root/scripts/install_redhat.sh $publish_root
echo "{\"build_id\":\"${BUILD_ID}\",\"git_commit\":\"${GIT_COMMIT}\",\"git_branch\":\"develop\"}" > $publish_root/build_info.json
sed -i -e  "s|/blackfly/blackfly.tar.gz|/blackfly/develop/blackfly.tar.gz|g" $publish_root/install.sh
sed -i -e  "s|/blackfly/blackfly.tar.gz|/blackfly/develop/blackfly.tar.gz|g" $publish_root/install_debian.sh
sed -i -e  "s|/blackfly/blackfly.tar.gz|/blackfly/develop/blackfly.tar.gz|g" $publish_root/install_redhat.sh

