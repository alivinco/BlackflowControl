import threading

from libs.iot_msg_lib.iot_msg_converter import IotMsgConverter

__author__ = 'aleksandrsl'
from libs import mosquitto
import logging
import time, socket

# import configs.log
# logging.config.dictConfig(configs.log.config)
log = logging.getLogger("bf_mqtt")


class MqttAdapter:
    def __init__(self, client_id="blackfly_test_suite", max_retry_attempt=15, retry_delay=15):
        """
        Contructor takes single argument which is reference to device registry object .
        :param device_registry:
        """
        self.retry_delay = retry_delay
        self._retry_counter = 0
        self._max_retry_attempts = max_retry_attempt
        self._thread = None
        self.sub_topics = ["jim1/evt/app/blackflow/+","jim1/evt/discovery"]
        self.topic_prefix = ""
        self.global_context = {}
        self.client_id = client_id
        self.mqtt = mosquitto.Mosquitto(self.client_id, clean_session=True)
        self.enable_sys = False

    def set_message_handler(self, on_message_handler):
        self.on_message = on_message_handler

    def set_mqtt_params(self, client_id, username="", password="", topic_prefix="", enable_sys=False):
        self.mqtt._client_id = client_id
        if topic_prefix:
            self.topic_prefix = topic_prefix+"/"

        self.enable_sys = enable_sys
        if username:
            self.mqtt.username_pw_set(username, password)

    def set_global_context(self, context):
        self.global_context = context

    def connect(self, host="localhost", port=1883, keepalive=60):
        """

        :param host:
        :param port:
        :param keepalive:
        :return: Return True in cases of success and False in case of failure
        """
        all_available_hosts = host.split(";")

        self._host = all_available_hosts[0]
        self._current_host_index = 0
        self._all_hosts = all_available_hosts
        self._port = port
        self._keepalive = keepalive
        self.mqtt.on_message = self._on_message
        self.mqtt.on_connect = self._on_connect
        # Try to connect to all available hosts in the list
        self.global_context['mqtt_conn_status'] = "offline"
        for i in xrange(len(all_available_hosts)):
            try:
                self.reconnect()
                log.info("BlackflyTestSuite connected to broker . host=" + self._host + " port=" + str(port))
                return True
            except Exception as ex:
                log.exception(ex)
        # False in case of connection failure
        return False

    def __get_next_host(self):
        number_of_available_hosts = len(self._all_hosts)
        index = self._current_host_index + 1
        if index < number_of_available_hosts:
            self._current_host_index = index
            return self._all_hosts[index]
        else:
            self._current_host_index = 0
            return self._all_hosts[0]

    def reconnect(self):
        self.mqtt.on_message = self._on_message
        self._host = self.__get_next_host()
        log.info("Reconnecting to broker , host = %s" % self._host)
        self.mqtt.connect(self._host, self._port, self._keepalive)
        self._retry_counter = 0
        log.info("The system reconnected to mqtt broker")

    def initiate_listeners(self):
        for topic in self.sub_topics:
            sub_topic = self.topic_prefix + topic
            self.mqtt.subscribe(sub_topic, 1)
            log.info("mqtt adapter subscribed to topic " + sub_topic)

    def stop_listeners(self):
        for topic in self.sub_topics:
            sub_topic = self.topic_prefix + topic
            self.mqtt.unsubscribe(sub_topic)
            log.info("mqtt adapter unsubscribed from topic " + sub_topic)


    def _on_connect(self, mosq, userdata, rc):
        if rc == 0:
            self.global_context['mqtt_conn_status'] = "online"

    def _on_message(self, mosq, obj, msg):

        """
        Callback mqtt message handler .
        :param mosq:
        :param obj:
        :param msg:
        """
        if self.topic_prefix:
            msg.topic = msg.topic.replace(self.topic_prefix, "")
        try:
            log.debug(msg.payload)
            self.on_message(msg.topic, IotMsgConverter.string_to_iot_msg(msg.topic, msg.payload))
        except Exception as ex:
            log.error("Exception during messages processing. The message from ropic " + msg.topic + " will be skipped")
            log.exception(ex)

    def publish(self, address, iot_msg, qos=1):
        topic = self.topic_prefix + address
        log.debug("Publishing msg to topic " + str(address))
        log.debug(iot_msg)
        self.mqtt.publish(topic, IotMsgConverter.iot_msg_with_topic_to_str(address,iot_msg) , qos)
        log.info("Message was published to topic = " + topic)

    def on_message(self, topic, iot_msg):
        log.info("do nothing and skipp the message")

    def _loop_start(self):
        if self._thread:
            if self._thread.isAlive():
                log.warn("Thread is already running . Only one thread loop is allowed")
                return None
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
                        rc = 1
                except Exception as ex:
                    log.error("Mqtt loop error")
                    log.exception(ex)
                    rc = 1

            if not self._thread_terminate:
                log.error("Loop interrupted because of error" + str(rc))
                self.global_context['mqtt_conn_status'] = "reconnecting"
                time.sleep(self.retry_delay)
                try:
                    self._retry_counter += 1
                    if self._retry_counter < self._max_retry_attempts:
                        log.info("Reconnecting to broker.....")
                        self.reconnect()
                        self.initiate_listeners()
                        log.info("Reconnection succeeded.")
                    else:
                        log.warn("The system has tried to reconnect for %s times without success.Going offline." % self._retry_counter)
                        self._thread_terminate = True
                        self.global_context['mqtt_conn_status'] = "offline"
                    rc = 0
                except socket.error as err:
                    self.global_context['mqtt_conn_status'] = "offline"
                    log.error("Reconnection attempt failed because of error : %s" % str(err))
                except Exception as err:
                    log.exception(err)
                    self.global_context['mqtt_conn_status'] = "offline"
                    log.error("Non recoverable error. Shutting down the adapter")
                    self._thread_terminate = True

    def start(self):
        self.initiate_listeners()
        log.info("Starting mqtt listener loop")
        self.global_context['mqtt_conn_status'] = "online"
        self._loop_start()

    def stop(self):
        self.stop_listeners()
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
