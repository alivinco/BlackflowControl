import json
from modules.mqtt_adapter import MqttAdapter
from modules.msg_manager import MessageManager

__author__ = 'aleksandrsl'

class App:

    def __init__(self,name,topic):
        self.context = {}
        self.name = name
        self.topic = topic
        self.msg_man = MessageManager()

    def init_mqtt(self):
        self.mqtt = MqttAdapter(None,self.msg_man.global_configs["mqtt"]["client_id"]+"_magic_"+self.name)
        self.mqtt.connect(self.msg_man.global_configs["mqtt"]["host"],int(self.msg_man.global_configs["mqtt"]["port"]))
        self.mqtt.sub_topic = self.topic
        self.mqtt.on_message = self.do_magic
        self.mqtt.start()

    def set_app_name(self,name):
        self.name = name
    # the class subscribes to topic /bftst/magic
    def do_magic(self,topic,json_msg):
        print "do your magic here"

    def send_message(self,topic,json_msg):
        """

        :param topic:
        :param json_msg:
        """
        self.mqtt.publish(topic,json.dumps(json_msg))





