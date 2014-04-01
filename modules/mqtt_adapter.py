import threading

__author__ = 'aleksandrsl'
from libs import mosquitto
import json
import logging
import time,socket
from configs import app

import configs.log
import logging,logging.config
logging.config.dictConfig(configs.log.config)
log = logging.getLogger("bf_mqtt")

class MqttAdapter:


    def __init__(self, msg_pipeline):
        """
        Contructor takes single argument which is reference to device registry object .
        :param device_registry:
        """
        self.retry_delay = 5
        self.sub_topic = "/#"
        self.mqtt = mosquitto.Mosquitto("blackfly_test_suite", clean_session=False)
        self.msg_pipeline = msg_pipeline

    def connect(self, host="localhost", port=1883, keepalive=60):
        self._host = host
        self._port = port
        self._keepalive = keepalive
        self.mqtt.on_message = self._on_message
        self.mqtt.connect(host, port, keepalive)
        log.info("BlackflyTestSuite connected to broker .")

    def initiate_listeners(self):

        self.mqtt.subscribe(self.sub_topic, 1)
        log.info("mqtt adapter subscribed to topic "+self.sub_topic)

    def _on_message(self, mosq, obj, msg):

        """
        Callback mqtt message handler .
        :param mosq:
        :param obj:
        :param msg:
        """
        if "command" in msg.topic:
            log.debug("Command type of message is skipped")
        else :
            log.info("New message from topic = "+str(msg.topic))
            self.msg_pipeline.process_event(msg.topic,json.loads(msg.payload))

    def _loop_start(self):
        self._thread_terminate = False
        self._thread = threading.Thread(target=self._thread_main)
        self._thread.daemon = True
        self._thread.start()
        log.info("Loop started")

    def _loop_stop(self):
        self._thread_terminate = True
        self._thread.join()
        self._thread = None
        log.info("Loop stopped")

    def _thread_main(self):
        rc = 0
        while not self._thread_terminate:
            while rc == 0:
                try:
                    rc = self.mqtt.loop()
                    if self._thread_terminate:
                        rc=1
                except Exception as ex:
                    log.error("Mqtt loop error")
                    log.exception(ex)
                    rc = 1

            if not self._thread_terminate :
                log.error("Loop interrupted because of error" + str(rc))
                time.sleep(self.retry_delay)
                try:
                    log.info("Reconnecting to broker.....")
                    self.connect(self._host, self._port, self._keepalive)
                    self.initiate_listeners()
                    log.info("Reconnection succeeded.")
                    rc = 0
                except socket.error as err:
                    log.error("Reconnection attempt failed because of error : %s"%str(err))
                except Exception as err:
                    log.exception(err)
                    log.error("Non recoverable error. Shutting down the adapter")
                    run = False


    def start(self):
        self.initiate_listeners()
        log.info("Starting mqtt listener loop")
        self._loop_start()


    def stop(self):
        log.info("Stopping mqtt listener loop")
        self.mqtt.disconnect()
        self._loop_stop()



if __name__ == "__main__":
    cache = None
    mqtt_ad = MqttAdapter(cache)
    mqtt_ad.connect("localhost", 1883)
    # mqtt_ad.mqtt.publish("/system/discovery",json.dumps(self.inclusion_msg),1)
    print "message published"
    # read binary

    mqtt_ad.start()
    time.sleep(5)
    mqtt_ad.stop()