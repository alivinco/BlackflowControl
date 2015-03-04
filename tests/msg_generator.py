import json
import time
from libs import mosquitto
import os
import threading
__author__ = 'aleksandrsl'


def generate_messages(name,count):
   mqtt = mosquitto.Mosquitto("blackfly_msg_generator_"+str(name), clean_session=True)
   mqtt.on_log = log
   mqtt.max_inflight_messages_set(20)
   mqtt.connect("alivinco.sg", 1883)
   # this is mosqutto application loop .
   mqtt.loop_start()
   f = open(os.path.join("messages","events","sensor.temperature.json"))
   fc = f.read()
   start_time = time.time()
   for i in range(0,count):
        mqtt.publish("/dev/test/1/sen_temp/1/events",fc,1)
        print "message %s was published "%i
        time.sleep(0.1)

   while  mqtt._inflight_messages > 0:
        print "Inflight messages :"+str(mqtt._inflight_messages)
        time.sleep(0.1)
   stop_time = time.time()

   print "Publish took %s sec to complete "%(stop_time-start_time)

   mqtt.disconnect()

   print "Thread "+str(name)+" copmleted."

def log(mosq, userdata, level, buf):
    pass

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


msg_sender(1000,1)
# generate_test_message()