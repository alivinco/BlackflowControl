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


    # address - topic address , payload - msg payload object
    def put(self,key,payload,ui_mapping,extracted_data):
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
        if id in self.cache:
            return self.cache[id]
        else :
            return None

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

    def clean_cache(self):
        self.cache = {}
        self.generic_cache = {}
        self.approve_cache = {}

if __name__ == "__main__":
    m = MessageManager()
    jobj = json.load(file(os.path.join(m.app_root_path,"messages","events","temperature.json") ))
    cache = MsgCache(m)
    cache.put("/zw/15/multilevel_sensor/1/events",jobj)
    cache.put("/zw/0/controller/1/events",json.load(file(os.path.join(m.app_root_path,"messages","events","inclusion.json") )))
    print json.dumps(cache.get_all(),indent=True)