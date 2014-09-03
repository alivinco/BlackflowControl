import threading

__author__ = 'aleksandrsl'
from libs import mosquitto
import json
import logging
import time,socket

# import configs.log
# logging.config.dictConfig(configs.log.config)
log = logging.getLogger("bf_mqtt")

class MqttAdapter:


    def __init__(self, msg_pipeline,client_id="blackfly_test_suite"):
        """
        Contructor takes single argument which is reference to device registry object .
        :param device_registry:
        """
        self.retry_delay = 5
        self.sub_topic = "/#"
        self.topic_prefix = ""
        self.global_context = {}
        self.mqtt = mosquitto.Mosquitto(client_id, clean_session=True)
        self.msg_pipeline = msg_pipeline
        self.enable_sys = False

    def set_mqtt_params(self,client_id,username="",password="",topic_prefix="",enable_sys=False):
        self.mqtt._client_id = client_id
        self.topic_prefix = topic_prefix
        self.enable_sys = enable_sys
        if username:
            self.mqtt.username_pw_set(username,password)

    def set_global_context(self,context):
        self.global_context = context

    def connect(self, host="localhost", port=1883, keepalive=60):
        self._host = host
        self._port = port
        self._keepalive = keepalive
        self.mqtt.on_message = self._on_message
        self.mqtt.on_connect = self._on_connect
        self.mqtt.connect(host, port, keepalive)
        self.global_context['mqtt_conn_status'] = "offline"
        log.info("BlackflyTestSuite connected to broker . host="+host+" port="+str(port))

    def reconnect(self):
        self.mqtt.on_message = self._on_message
        self.mqtt.connect(self._host, self._port, self._keepalive)
        log.info("The system reconnected to mqtt broker")

    def initiate_listeners(self):
        topic = self.topic_prefix+self.sub_topic
        self.mqtt.subscribe(topic, 1)
        # mosquitto internal monitoring topic
        if self.enable_sys :
            self.mqtt.subscribe("$SYS/#",1)
            log.info("mqtt adapter subscribed to $SYS/# mqtt internal monitoring topic.")
        log.info("mqtt adapter subscribed to topic "+topic)

    def _on_connect(self, mosq, userdata, rc):
        if rc == 0 :
           self.global_context['mqtt_conn_status'] = "online"

    def _on_message(self, mosq, obj, msg):

        """
        Callback mqtt message handler .
        :param mosq:
        :param obj:
        :param msg:
        """
        if "$SYS" in msg.topic:
           if self.msg_pipeline:
               self.msg_pipeline.process_event(msg.topic,msg.payload)

        # elif "command" in msg.topic:
        #     log.debug("Command type of message is skipped")

        else :
            log.info("New message from topic = "+str(msg.topic))
            log.debug(msg.payload)
            msg_obj = None
            if self.msg_pipeline:
                try:
                  msg_obj = json.loads(msg.payload)
                except Exception as ex :
                  log.error("The message can't be recognized as json object and therefore ignored.")
                if msg_obj : self.msg_pipeline.process_event(msg.topic,msg_obj)
            else :
                self.on_message(msg.topic,msg.payload)
    def publish(self,address,payload,qos):
        topic = self.topic_prefix+address
        log.debug("Publishing msg to topic "+str(address))
        log.debug(payload)
        self.mqtt.publish(topic,payload,qos)
        log.info("Message was published to topic = "+topic)

    def on_message(self,topic,json_msg):
        log.info("do nothing and skipp the message")

    def _loop_start(self):
        self._thread_terminate = False
        self._thread = threading.Thread(target=self._thread_main)
        self._thread.daemon = True
        self._thread.start()
        self.global_context['mqtt_conn_status'] = "online"
        log.info("Loop started")

    def _loop_stop(self):
        self._thread_terminate = True
        self._thread.join()
        self._thread = None
        self.global_context['mqtt_conn_status'] = "offline"
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
                self.global_context['mqtt_conn_status'] = "reconnecting"
                time.sleep(self.retry_delay)
                try:
                    log.info("Reconnecting to broker.....")
                    self.connect(self._host, self._port, self._keepalive)
                    self.initiate_listeners()
                    log.info("Reconnection succeeded.")
                    rc = 0
                except socket.error as err:
                    self.global_context['mqtt_conn_status'] = "offline"
                    log.error("Reconnection attempt failed because of error : %s"%str(err))
                except Exception as err:
                    log.exception(err)
                    self.global_context['mqtt_conn_status'] = "offline"
                    log.error("Non recoverable error. Shutting down the adapter")
                    run = False


    def start(self):
        self.initiate_listeners()
        log.info("Starting mqtt listener loop")
        self.global_context['mqtt_conn_status'] = "online"
        self._loop_start()


    def stop(self):
        log.info("Stopping mqtt listener loop")
        self.mqtt.disconnect()
        self.global_context['mqtt_conn_status'] = "offline"
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