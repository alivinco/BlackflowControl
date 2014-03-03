import threading

__author__ = 'aleksandrsl'
from libs import mosquitto
import json
import logging
import time,socket
from configs import app

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())


class MqttAdapter:
    logger = logging.getLogger(__name__)

    def __init__(self, msg_pipeline):
        """
        Contructor takes single argument which is reference to device registry object .
        :param device_registry:
        """
        self.retry_delay = 5
        self.logger.setLevel(logging.DEBUG)
        self.mqtt = mosquitto.Mosquitto("blackfly_test_suite", clean_session=False)
        self.msg_pipeline = msg_pipeline

    def connect(self, host="localhost", port=1883, keepalive=60):
        self._host = host
        self._port = port
        self._keepalive = keepalive
        self.mqtt.on_message = self._on_message
        self.mqtt.connect(host, port, keepalive)
        self.logger.debug("DR connected to broker .")

    def initiate_listeners(self):
        self.mqtt.subscribe("#", 1)


    def _on_message(self, mosq, obj, msg):

        """
        Callback mqtt message handler .
        :param mosq:
        :param obj:
        :param msg:
        """
        self.logger.debug("New message :" + str(msg))
        self.msg_pipeline.process_event(msg.topic,json.loads(msg.payload))

    def _loop_start(self):
        self._thread_terminate = False
        self._thread = threading.Thread(target=self._thread_main)
        self._thread.daemon = True
        self._thread.start()

    def _loop_stop(self):
        self._thread_terminate = True
        self._thread.join()
        self._thread = None

    def _thread_main(self):
        rc = 0
        while not self._thread_terminate:
            while rc == 0:
                rc = self.mqtt.loop()
                if self._thread_terminate:
                    rc=1
            if not self._thread_terminate :
                self.logger.error("Loop interrupted because of error" + str(rc))
                time.sleep(self.retry_delay)
                try:
                    self.logger.info("Reconnecting to broker.....")
                    self.connect(self._host, self._port, self._keepalive)
                    self.initiate_listeners()
                    self.logger.info("Reconnection succeeded.")
                    rc = 0
                except socket.error as err:
                    self.logger.error("Reconnection attempt failed because of error : %s"%str(err))
                except Exception as err:
                    self.logger.error(err)
                    self.logger.error("Non recoverable error. Shutting down the adapter")
                    run = False


    def start(self):
        self.initiate_listeners()
        self._loop_start()
        self.logger.info("Mqtt loop started")

    def stop(self):
        self.mqtt.disconnect()
        self._loop_stop()
        self.logger.info("DR disconnected from mqtt broker")


if __name__ == "__main__":
    cache = None
    mqtt_ad = MqttAdapter(cache)
    mqtt_ad.connect("localhost", 1883)
    # mqtt_ad.mqtt.publish("/system/discovery",json.dumps(self.inclusion_msg),1)
    print "message published"

    mqtt_ad.start()
    time.sleep(5)
    mqtt_ad.stop()