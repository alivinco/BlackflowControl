from Queue import Queue
import logging.config
import threading
from unittest import TestCase
import time
import thread
import configs.log
from libs.sync_to_async_msg_converter import SyncToAsyncMsgConverter
from modules.mqtt_adapter import MqttAdapter
import json

__author__ = 'alivinco'

logging.config.dictConfig(configs.log.config)

REQUEST_TOPIC = "/app/test/sync_async_test/commands"
RESPONSE_TOPIC = "/app/test/sync_async_test/events"

class MqttAdapterForTest(MqttAdapter):

    def _on_message(self, mosq, obj, msg):

        print "**** New message ***********"
        msg_obj = json.loads(msg.payload)
        if "commands" in msg.topic:
            self.responder(msg.topic, msg_obj)
        else :
            self.sync_async_conv.on_message(msg.topic, msg_obj)


    def set_sync_converter(self, sync_conv):
        self.sync_async_conv = sync_conv

    def responder(self, topic, msg):
        self.publish(RESPONSE_TOPIC,json.dumps(msg),1)
        print "Response was sent."

class SenderClient(threading.Thread):

    def __init__(self,conv,name,corr_id):
        super(SenderClient, self).__init__(name=name)
        self.corr_id = corr_id
        self.name = name
        self.conv = conv
        self.result_queue = Queue()

    def run(self):

        msg = {"payload": "test" + self.name, "corid": self.name}
        print "Test 1 .Waiting for response .Correlation id is provided Test id = "+self.name
        resp = self.conv.send_sync_msg(msg, REQUEST_TOPIC, RESPONSE_TOPIC, 10 ,generate_corrid=True)
        if not resp : self.result_queue.put("fail")
        print "Test 1 Response : test id = " + self.name + " response msg = " + str(resp)

        msg = {"payload": "test" + self.name }
        print "Test 2 .Waiting for response .Correlation id is generated Test id = "+self.name
        resp = self.conv.send_sync_msg(msg, REQUEST_TOPIC, RESPONSE_TOPIC, 10 ,generate_corrid=True)
        if not resp : self.result_queue.put("fail")
        print "Test 2 .Response  test : test id = " + self.name + " response msg = " + str(resp)

        msg = {"event": {"default": { "value": self.name },"subtype": "generic","@type": "binary"} }
        print "Test 3 .Waiting for response .Correlation is msg type and topic "+self.name
        resp = self.conv.send_sync_msg(msg, REQUEST_TOPIC, RESPONSE_TOPIC, 10 ,generate_corrid=False,correlation_type="MSG_TYPE",correlation_msg_type="binary.generic")
        if not resp : self.result_queue.put("fail")
        print "Test 3 .Response  test : test id = " + self.name + " response msg = " + str(resp)

        msg = {"event": {"default": { "value": self.name },"subtype": "switch","@type": "binary"} }
        print "Test 4 .Waiting for response .Correlation is msg type and topic "+self.name
        resp = self.conv.send_sync_msg(msg, REQUEST_TOPIC, RESPONSE_TOPIC, 10 ,generate_corrid=False,correlation_type="MSG_TYPE",correlation_msg_type="binary.switch")
        if not resp : self.result_queue.put("fail")
        print "Test 4 .Response  test : test id = " + self.name + " response msg = " + str(resp)
        self.result_queue.put("ok")

class TestSyncToAsyncMsgConverter(TestCase):
    @classmethod
    def setUpClass(cls):
        cache = None
        cls.mqtt_ad = MqttAdapterForTest(cache,client_id="AsyncToSyncConverterTest")
        cls.mqtt_ad.connect("localhost", 1883)
        cls.mqtt_ad.sub_topic = "/app/test/sync_async_test/#"

        cls.conv = SyncToAsyncMsgConverter(cls.mqtt_ad)
        cls.mqtt_ad.set_sync_converter(cls.conv)
        cls.mqtt_ad.start()


    def test_send_sync_msg(self):
        # Running each request in it's own thread

        for item in range(5):
            t1 = SenderClient(self.conv,str(item),"str_id_"+str(item))
            t1.start()
            if t1.result_queue.get(10)=="fail": self.fail("send_assync_fail")

    def test_sync_wait_for_msg(self):
        def send_event():
            time.sleep(1)
            msg = {"event": {"default": { "value": "STAGE_STARTING_INTERVIEW" },"subtype": "inclusion_stage","@type": "zw_ta"} }
            self.mqtt_ad.publish("/app/test/sync_async_test/sync_wait/events",json.dumps(msg),1)

        thread.start_new_thread(send_event,())
        if not self.conv.sync_wait_for_msg("/app/test/sync_async_test/sync_wait/events","MSG_TYPE","zw_ta.inclusion_stage",10) :
            self.fail()
        # time.sleep(10)






