FROM python:2.7.11-alpine
MAINTAINER Aleksandrs.Livincovs@gmail.com
ADD ./ /opt/BlackflowControl
WORKDIR /opt/BlackflowControl
RUN apk --no-cache add ca-certificates && update-ca-certificates
RUN pip install flask requests auth0-python
ENV AUTH0_CLIENT_ID=""
CMD python BlackflowControl.py -c configs/global.json --authclientid $AUTH0_CLIENT_ID
EXPOSE 5001
