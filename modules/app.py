import json
from modules.mqtt_adapter import MqttAdapter
from modules.msg_manager import MessageManager

__author__ = 'aleksandrsl'

class App:

    global_app_context = {"app_counter":0}

    def __init__(self,name,topics):
        self.global_app_context["app_counter"] = self.global_app_context["app_counter"]+1
        self.context = {}
        self.name = name
        self.topics = topics
        self.msg_man = MessageManager()

    def init_mqtt(self):
        self.mqtt = MqttAdapter(None,self.msg_man.global_configs["mqtt"]["client_id"]+"_app_"+self.name)
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

    def start(self):
        """
        method start application

        """
        pass

    def stop(self):
        """
        method stops application

        """
        pass

    def get_state(self):

        """
        method returns application state

        """
        pass


    def control(self,name,value):
        """
        method controls application via setting control parameters
        :param name:
        :param value:
        """
        pass




