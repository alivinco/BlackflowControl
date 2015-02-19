import json
import time
from libs import mosquitto
import os
import threading
__author__ = 'aleksandrsl'


def generate_messages(name,count):
   mqtt = mosquitto.Mosquitto("blackfly_msg_generator_"+str(name), clean_session=True)
   mqtt.max_inflight_messages_set(count+1)
   mqtt.connect("sg.st", 1883)
   f = open(os.path.join("messages","events","meter.power.json"))
   fc = f.read()
   for i in range(0,count):
        mqtt.publish("/dev/serial/test_id/met_power/1/events",fc,1)

   while  mqtt._inflight_messages > 0:
       print "Inflight messages :"+str(mqtt._inflight_messages)
       time.sleep(1)

   mqtt.disconnect()

   print "Thread "+str(name)+" copmleted."

def msg_sender(msg_total,num_of_threads):
    msg_per_thread = msg_total//num_of_threads
    msg_for_last_thread = msg_total%num_of_threads
    threads = []
    for i in range(0, num_of_threads):
        print "Thread nr:"+str(i)
        t1 = threading.Thread(target=generate_messages,args=(i,msg_per_thread))
        t1.start()
        threads.append(t1)
    print "Waiting for threads completion"
    for t in threads:
        t.join()
    print "Done"


msg_sender(100,1)
# generate_test_message()