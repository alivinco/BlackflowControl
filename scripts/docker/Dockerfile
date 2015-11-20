#FROM ubuntu:14.04
FROM debian:jessie
MAINTAINER Aleksandrs.Livincovs@gmail.com
# Update the sources list
RUN apt-get update;apt-get install -y python;apt-get clean

ADD ./ /tmp/BlackflyTestSuite

RUN cd /tmp/BlackflyTestSuite;chmod a+x setup_debian.sh; sync;./setup_debian.sh

WORKDIR /opt/BlackflyTestSuite

CMD python BlackflyTestSuite.py

EXPOSE 5000
