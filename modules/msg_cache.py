from modules.msg_manager import MessageManager
import json , os
from datetime import datetime
__author__ = 'aleksandrsl'


class MsgCache():
    def __init__(self,msg_man):
        self.cache = {}
        self.generic_cache = {}
        self.approve_cache = {}
        self.msg_man = msg_man
        self.address_mapping = self.msg_man.load_address_mapping()
        self.msg_class_mapping = self.msg_man.load_msg_class_mapping()


    # address - topic address , payload - msg payload object
    def put(self,key,payload,ui_mapping,extracted_data):
        # if "event" in payload:
        #   path = self.msg_man.msg_class_path_event
        #   msg_type = "event"
        # else :
        #   path = self.msg_man.msg_class_path_command
        #   msg_type = "command"
        #
        # msg_class = self.msg_man.get_value_from_msg(payload,path)[0]
        # id = self.msg_man.generate_key(msg_class,address)
        #
        # # extract values
        # extracted_values = {}
        # ui_mapping = {}
        # try:
        #     ui_mapping = self.msg_man.get_msg_class_by_key(id)["ui_mapping"]
        #     for key,value in ui_mapping.items():
        #         if "path" in key:
        #             print "trying to extract value from "+value
        #             ex_value = self.msg_man.get_value_from_msg(payload,value)[0]
        #             extracted_values[key.replace("_path","")]=ex_value
        # except Exception as ex :
        #     #default value
        #     ui_mapping["ui_element"] = {"ui_element":"free_text","value_path":"$.event.value"}
        #     print "Can't extract value"
        timestamp_iso = datetime.now().isoformat()
        self.cache[key]={"raw_msg":payload,"ui_element":ui_mapping["ui_element"],"extracted_values":extracted_data,"timestamp_iso":timestamp_iso}

    def put_generic(self,key,value):
        timestamp_iso = datetime.now().isoformat()
        self.generic_cache[key] = {"raw_msg":value,"timestamp_iso":timestamp_iso}

    def get_all(self,exclude_raw_msg=False):
        result = {}
        if exclude_raw_msg:
           for key,item in self.cache.iteritems() :
              result[key]={"ui_element":item["ui_element"],"extracted_values":item["extracted_values"],"timestamp_iso":item["timestamp_iso"]}
           return result
        else :
           return self.cache

    def get_all_generic(self):
        return self.generic_cache

    def get(self,msg_class,address):
        id = self.msg_man.generate_key(msg_class,address)
        return self.cache[id]

    def get_generic(self,key):
        return self.generic_cache[key]

    def get_by_key(self,key):
        if self.cache.has_key(key):
          return self.cache[key]
        else :
          return None

    def put_msg_class_for_approval(self,address,payload,msg_class,text):
        id = self.msg_man.generate_key(msg_class,address)
        timestamp_iso = datetime.now().isoformat()
        self.approve_cache[id] = {"address":address,"payload":json.dumps(payload,indent=True),"msg_class":msg_class,"text":text,"timestamp_iso":timestamp_iso}

    def remove_msg_clas_for_approval(self,key):
        del self.approve_cache[key]

    def get_approval_list(self):
        return self.approve_cache





if __name__ == "__main__":
    m = MessageManager()
    jobj = json.load(file(os.path.join(m.app_root_path,"messages","events","temperature.json") ))
    cache = MsgCache(m)
    cache.put("/zw/15/multilevel_sensor/1/events",jobj)
    cache.put("/zw/0/controller/1/events",json.load(file(os.path.join(m.app_root_path,"messages","events","inclusion.json") )))
    print json.dumps(cache.get_all(),indent=True)