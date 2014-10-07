#!/bin/sh

BF_ROOT=/opt/BlackflyTestSuite
# Creating user
echo "Adding blackfly user and group"
useradd -r -m -d /var/lib/blackfly -s /usr/sbin/nologin blackfly

# Checking existing installation
if [ -d $BF_ROOT ]
then
 echo "The script found current installation and is doing backup of config folder"
 service blackfly stop
 cp -r $BF_ROOT/configs /tmp
 cp -r $BF_ROOT/messages/events /tmp
 echo "The config folder copied to /tmp/configs"
 echo "Removing blackfly isntallation"
 rm -r $BF_ROOT
 is_upgrade=1
else
 is_upgrade=0
fi

echo "Creating $BF_ROOT folder"
mkdir $BF_ROOT
cp -r * $BF_ROOT
cd $BF_ROOT
# Flask installation
check_flask=$(python -c "import flask;print 'ok'")
if [ "$check_flask" = "ok" ]
then
  echo "The script found flask module"
else
  echo "The script can't find flask module . It will be installed"
  python scripts/get-pip.py
  pip install Flask
fi

echo "Copying init scripts"
chmod a+x scripts/etc/init.d/blackfly_debian
chmod a+x BlackflyTestSuite.py
cp  scripts/etc/init.d/blackfly_debian /etc/init.d/blackfly
cp  scripts/configs/log_debian.py configs/log.py

# Creating log dir
mkdir /var/log/blackfly
chown blackfly:blackfly /var/log/blackfly


# address mapping replaced by fresh address mapping
if [ $is_upgrade = 1 ]
then
 echo "Copying address_mapping.json and global.json from previous installation"
 cp /tmp/configs/address_mapping.json configs/
 cp /tmp/configs/global.json configs/
 cp -r /tmp/events messages/
 echo "Running update script"
 python scripts/upgrade.py
else
 echo "Copying default address_mapping.json"
 cp  scripts/configs/address_mapping.json configs/
fi

# Make sure blackfly user owns the directory
chown -R blackfly:blackfly $BF_ROOT

# updating global.json config
echo "Updating global.json config file"
python scripts/cmd_update_config.py --file configs/global.json --jpath db.db_path --value /var/lib/blackfly/timeseries.db

update-rc.d blackfly defaults 90
echo "Starting blackfly daemon..."
service blackfly start

