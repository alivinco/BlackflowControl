import logging.config
import threading
from unittest import TestCase
import time
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

    def run(self):
        msg = {"payload": "test" + self.name, "corid": self.name}
        print "Test 1 .Waiting for response .Correlation id is provided Test id = "+self.name
        resp = self.conv.send_sync_msg(msg, REQUEST_TOPIC, RESPONSE_TOPIC, 10 ,generate_corrid=True)
        print "Test 1 Response : test id = " + self.name + " response msg = " + str(resp)

        msg = {"payload": "test" + self.name }
        print "Test 2 .Waiting for response .Correlation id is generated Test id = "+self.name
        resp = self.conv.send_sync_msg(msg, REQUEST_TOPIC, RESPONSE_TOPIC, 10 ,generate_corrid=True)
        print "Test 2 .Response  test : test id = " + self.name + " response msg = " + str(resp)

        msg = {"event": {"default": { "value": self.name },"subtype": "generic","@type": "binary"} }
        print "Test 3 .Waiting for response .Correlation is msg type and topic "+self.name
        resp = self.conv.send_sync_msg(msg, REQUEST_TOPIC, RESPONSE_TOPIC, 10 ,generate_corrid=False,correlation_type="MSG_TYPE",correlation_msg_type="binary.generic")
        print "Test 3 .Response  test : test id = " + self.name + " response msg = " + str(resp)

        msg = {"event": {"default": { "value": self.name },"subtype": "switch","@type": "binary"} }
        print "Test 4 .Waiting for response .Correlation is msg type and topic "+self.name
        resp = self.conv.send_sync_msg(msg, REQUEST_TOPIC, RESPONSE_TOPIC, 10 ,generate_corrid=False,correlation_type="MSG_TYPE",correlation_msg_type="binary.switch")
        print "Test 4 .Response  test : test id = " + self.name + " response msg = " + str(resp)

class TestSyncToAsyncMsgConverter(TestCase):
    def setUp(self):
        cache = None
        self.mqtt_ad = MqttAdapterForTest(cache,client_id="AsyncToSyncConverterTest")
        self.mqtt_ad.connect("lego.r", 1883)
        self.mqtt_ad.sub_topic = "/app/test/sync_async_test/+"


        self.conv = SyncToAsyncMsgConverter(self.mqtt_ad)
        self.mqtt_ad.set_sync_converter(self.conv)
        self.mqtt_ad.start()

    def test_send_sync_msg(self):
        # Running each request in it's own thread

        for item in range(5):
            t1 = SenderClient(self.conv,str(item),"str_id_"+str(item))
            t1.start()

        # time.sleep(10)






