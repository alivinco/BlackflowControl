#!/bin/sh
mount - / -oremount,rw
python scripts/get-pip.py
pip install Flask
chmod a+x scripts/etc/init.d/blackfly
chmod a+x BlackflyTestSuite.py
cp -i scripts/etc/init.d/blackfly /etc/init.d/
cp -i scripts/configs/log.py configs/
# address mapping replaced by fresh address mapping
cp -i scripts/configs/address_mapping.json configs/
update-rc.d blackfly defaults 90

