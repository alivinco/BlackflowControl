from modules.msg_manager import MessageManager
import json , os
__author__ = 'aleksandrsl'


class MsgCache():
    def __init__(self,msg_man):
        self.cache = {}
        self.msg_man = msg_man
        self.address_mapping = self.msg_man.load_address_mapping()
        self.msg_class_mapping = self.msg_man.load_msg_class_mapping()

    # address - topic address , payload - msg payload object
    def put(self,address,payload):
        if "event" in payload:
          path = self.msg_man.msg_class_path_event
          msg_type = "event"
        else :
          path = self.msg_man.msg_class_path_command
          msg_type = "command"

        msg_class = self.msg_man.get_value_from_msg(payload,path)[0]
        id = self.msg_man.generate_key(msg_class,address)

        # extract values
        extracted_values = {}
        ui_mapping = {}
        try:
            ui_mapping = self.msg_man.get_msg_class_by_key(id)["ui_mapping"]
            for key,value in ui_mapping.items():
                if "path" in key:
                    print "trying to extract value from "+value
                    ex_value = self.msg_man.get_value_from_msg(payload,value)[0]
                    extracted_values[key.replace("_path","")]=ex_value
        except Exception as ex :
            #default value
            ui_mapping["ui_element"] = {"ui_element":"free_text","value_path":"$.event.value"}
            print "Can't extract value"

        self.cache[id]={"raw_msg":payload,"ui_element":ui_mapping["ui_element"],"extracted_values":extracted_values}


    def get_all(self):
        return self.cache

    def get(self,msg_class,address):
        id = self.msg_man.generate_key(msg_class,address)
        return self.cache(id)

    def get_by_key(self,key):
        if self.cache.has_key(key):
          return self.cache[key]
        else :
          return None

if __name__ == "__main__":
    m = MessageManager()
    jobj = json.load(file(os.path.join(m.app_root_path,"messages","events","temperature.json") ))
    cache = MsgCache(m)
    cache.put("/zw/15/multilevel_sensor/1/events",jobj)
    cache.put("/zw/0/controller/1/events",json.load(file(os.path.join(m.app_root_path,"messages","events","inclusion.json") )))
    print json.dumps(cache.get_all(),indent=True)