#!/bin/sh
mount - / -oremount,rw
curl -o /tmp/get-pip.py https://raw.github.com/pypa/pip/master/contrib/get-pip.py
cd /tmp
python get-pip.py
pip install Flask