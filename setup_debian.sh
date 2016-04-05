#!/bin/sh

BF_ROOT=/opt/BlackflowControl
# Creating user
echo "Adding blackfly user and group"
useradd -r -m -d /var/lib/blackfly -s /usr/sbin/nologin bfctrl

# Checking existing installation
if [ -d $BF_ROOT ]
then
 echo "The script found current installation and is doing backup of config folder"
 service bfctrl stop
 cp -r $BF_ROOT/configs /tmp
 cp -r $BF_ROOT/messages/events /tmp
 echo "The config folder copied to /tmp/configs"
 echo "Removing bfctrl isntallation"
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
pip install influxdb
pip install pyRFC3339

echo "Copying init scripts"
chmod a+x scripts/etc/init.d/bfctrl_debian
chmod a+x BlackflowControl.py
cp  scripts/etc/init.d/bfctrl_debian /etc/init.d/bfctrl
cp  scripts/configs/log_debian.py configs/log.py

# Creating log dir
mkdir /var/log/bfctrl
chown bfctrl:bfctrl /var/log/bfctrl


# address mapping replaced by fresh address mapping
if [ $is_upgrade = 1 ]
then
 echo "Copying address_mapping.json and global.json from previous installation"
 cp /tmp/configs/global.json configs/
 if [ -e "/tmp/configs/users.json" ];
    then
        cp /tmp/configs/users.json configs/
    else
        cp  scripts/configs/users.json configs/
 fi
 echo "Running update script"
 python scripts/upgrade.py
else
 echo "Copying default address_mapping.json"
 cp  scripts/configs/users.json configs/
fi

# Make sure bfctrl user owns the directory
chown -R bfctrl:bfctrl $BF_ROOT

# updating global.json config
echo "Updating global.json config file"
python scripts/cmd_update_config.py --file configs/global.json --jpath system.platform --value debian

update-rc.d bfctrl defaults 90
echo "Starting bfctrl daemon..."
service bfctrl start

