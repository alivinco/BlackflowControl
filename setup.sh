#!/bin/sh
BLACK_DIR = $(pwd)
mount - / -oremount,rw
curl -o /tmp/get-pip.py https://raw.github.com/pypa/pip/master/contrib/get-pip.py
cd /tmp
python get-pip.py
pip install Flask
cd $BLACK_DIR
chmod a+x scripts/etc/init.d/blackfly
cp -i scripts/etc/init.d/blackfly /etc/init.d/
cp -i sripts/log.py configs/
update-rc.d blackfly defaults
