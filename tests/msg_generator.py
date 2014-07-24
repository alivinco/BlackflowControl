import json
import time
from libs import mosquitto
import os
__author__ = 'aleksandrsl'



def send(topic,msg):
     mqtt = mosquitto.Mosquitto("blackfly_msg_generator", clean_session=False)
     mqtt.connect("localhost", 1883)
     mqtt.publish(topic,msg,1)
     time.sleep(1)
     mqtt.disconnect()

def generate_message():
   # send("/zw/3/binary_switch/1/commands",json.dumps(msg))
   f = open(os.path.join("messages","events","meter.power.json"))
   send("/dev/serial/1243423/met_power/1/events",f.read())

def generate_test_message():
   f = open(os.path.join("tests","msg","test.test2.json"))
   send("/dev/test/2/tst_test/1/events",f.read())
   f.close()

generate_message()
# generate_test_message()