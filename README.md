## BlackflowControl overview 

### Configuration 

####Using config file
  BlackflowControl instance is configurable via globals.json . By default the app will search the file in config folder , default value can be overridden using -c command line parameters 
  for instance : 
  
  `python BlackflowControl.py -c /etc/blackflowcontrol/global.json`


#### Docker 
Build container : 
````
docker build -t alivinco/blackflowcontrol .
or 
make dist-docker
````

Publish : 
````
docker push alivinco/blackflowcontrol
or 
make docker-publish
````

