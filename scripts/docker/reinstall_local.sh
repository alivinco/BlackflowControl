#!/usr/bin/env bash
pname = alivinco/blackfly
docker stop $pname
docker rm $pname
docker run --name blackfly -p 5001:5000 -d -e VIRTUAL_HOST=blackfly $pname


