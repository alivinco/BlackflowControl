#!/bin/sh

BF_ROOT=/media/app/BlackFlyTestSuite
mount - / -oremount,rw
# Check existing installation
if [ -d $BF_ROOT ]
then
 echo "The script found current installation and is doing backup of config folder"
 cp $BF_ROOT/configs /tmp
 echo "The config folder copied to /tmp/config"
 echo "Removing blackfly isntallation"
 rm -r BF_ROOT
 is_upgrade=1
else
 is_upgrade=0
fi
echo "Creating $BF_ROOT folder"
mkdir $BF_ROOT
cp -r * $BF_ROOT
cd $BF_ROOT
# Flask installation
check_flask=$(python -c "import flask")
if [ "$check_flask" = "" ]
then
  echo "The script found flask module"
else
  echo "The script can't find flask module . It will be installed"
  python scripts/get-pip.py
  pip install Flask
fi

chmod a+x scripts/etc/init.d/blackfly
chmod a+x BlackflyTestSuite.py
cp  scripts/etc/init.d/blackfly /etc/init.d/
cp  scripts/configs/log.py configs/
# address mapping replaced by fresh address mapping
if [ $is_upgrade = 1 ]
then
 echo "Copying address_mapping.json and global.json from previous installation"
 cp /tmp/configs/address_mapping.json configs/
 cp /tmp/configs/global.json configs/
 echo "Running update script"
 python scripts/update.py
else
 echo "Copying default address_mapping.json"
 cp  scripts/configs/address_mapping.json configs/
fi
update-rc.d blackfly defaults 90
mount - / -oremount,ro
echo "Starting blackfly daemon"
service blackfly start

