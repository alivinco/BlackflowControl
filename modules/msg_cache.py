from modules.msg_manager import MessageManager
import json , os
__author__ = 'aleksandrsl'


class MsgCache():
    def __init__(self,msg_man):
        self.cache = {}
        self.msg_man = msg_man
        self.address_mapping = self.msg_man.load_address_mapping()

    def put(self,address,payload,type):
        if type =="event":
          path = self.msg_man.msg_class_path_event
        else :
          path = self.msg_man.msg_class_path_command

        msg_class = self.msg_man.get_value_from_msg(payload,path)[0]
        id = self.msg_man.generate_id(msg_class,address)
        self.cache[id]=payload

    def get_all(self):
        return self.cache

if __name__ == "__main__":
    m = MessageManager()
    jobj = json.load(file(os.path.join(m.root,"messages","events","temperature_sensor.json") ))
    cache = MsgCache(m)
    cache.put("/zw/15/multilevel_sensor/1/events",jobj,"event")
    print cache.get_all()