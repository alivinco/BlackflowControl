import json
import time
from libs import mosquitto

__author__ = 'aleksandrsl'



def send(topic,msg):
     mqtt = mosquitto.Mosquitto("blackfly_msg_generator", clean_session=False)
     mqtt.connect("192.168.31.252", 1883)
     mqtt.publish(topic,msg,1)
     time.sleep(1)
     mqtt.disconnect()

def generate_new_type():
   msg = {"event":{"type":"brand_new_type","value":136,"units":"ccc"}}
   # send("/zw/3/binary_switch/1/commands",json.dumps(msg))
   send("/zw/3/binary_switch/1/commands","")


generate_new_type()
