#!/usr/bin/env bash
pname = alivinco/blackfly
docker stop $pname
docker rm $pname
sudo docker run --name nginx-master -d -t -p 80:80 -p 443:443 -v /etc/ssl/private/:/etc/nginx/certs -v /var/run/docker.sock:/tmp/docker.sock:ro alivinco/nginx-proxy


