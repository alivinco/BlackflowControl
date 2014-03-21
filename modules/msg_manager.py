__author__ = 'aleksandrsl'
import os
import json
from libs import jsonpath
import copy

import configs.log
import logging,logging.config
logging.config.dictConfig(configs.log.config)
log = logging.getLogger("bf_web")

# msg_list = {"events": ["file_name"], "commands": ["file_name"]}
msg_list = [{"file_name": "inclusion.json", "type": "event"}]


class MessageManager:
    def __init__(self):
        self.app_root_path = os.getcwd()
        self.events_dir = os.path.join(self.app_root_path, "messages", "events")
        self.commands_dir = os.path.join(self.app_root_path, "messages", "commands")
        self.msg_class_mapping_file_path = os.path.join(self.app_root_path, "configs", "msg_class_mapping.json")
        self.address_mapping_file_path = os.path.join(self.app_root_path, "configs", "address_mapping.json")
        self.msg_class_mapping = self.load_msg_class_mapping()
        self.address_mapping = self.load_address_mapping()
        self.global_configs = json.load(file(os.path.join(self.app_root_path, "configs", "global.json")))

    def load_templates(self):

        msg_list = []
        for file in os.listdir(self.events_dir):
            msg_list.append({"file_name": file, "type": "event"})
        for file in os.listdir(self.commands_dir):
            msg_list.append({"file_name": file, "type": "command"})

        return msg_list
    def get_msg_class_by_key(self,msg_key):
        split_str = msg_key.split("@")
        msg_class = split_str[0]
        address = split_str[1]

        if "event" in address: msg_type = "event"
        elif "commands" in address: msg_type = "command"
        else:
            log.info("the system can't identify message type , default value 'event' will be set")
            msg_type = "event"

        return filter(lambda map_item: (map_item["msg_class"] == msg_class and map_item["msg_type"]==msg_type) ,self.msg_class_mapping)[0]

    def add_msg_class(self,msg_class,msg_type,ui_element=None,value_path=None):

        #define default values
        default_path = ""
        if msg_type == "command":
            default_path = self.global_configs["defaults"]["cmd_value_path_for_new_class"]
        elif msg_type == "event":
            default_path = self.global_configs["defaults"]["event_value_path_for_new_class"]

        new_class = {"msg_class":msg_class,"msg_type":msg_type,"ui_mapping":{"ui_element":"free_text","value_path":default_path}}

        self.msg_class_mapping.append(new_class)
        # let's serialize the updated structure
        # f = open(self.msg_class_mapping_file_path,"w")
        json.dump(self.msg_class_mapping,open(self.msg_class_mapping_file_path,"w"),indent=True)

    def load_template_by_key(self,msg_key):
        msg_class = msg_key.split("@")[0]
        address = msg_key.split("@")[1]
        result = None
        if "event" in address:
           result = json.load(file(os.path.join(self.app_root_path, "messages","events", msg_class+".json")))
        elif "command" in address:
            result = json.load(file(os.path.join(self.app_root_path, "messages","commands", msg_class+".json")))
        else : result = None
        return result

    def load_msg_class_mapping(self):
        jobj = json.load(file(self.msg_class_mapping_file_path))
        return jobj

    def load_address_mapping(self):
        jobj = json.load(file(self.address_mapping_file_path))
        return jobj

    def reload_all_mappings(self):
        self.msg_class_mapping = self.load_msg_class_mapping()
        self.address_mapping = self.load_address_mapping()

    def generate_key(self,msg_class,address):
        return msg_class+"@"+address.replace("/",".")

    def generate_linked_mapping(self,msg_class_mapping,address_mapping):
        mapping = copy.copy(address_mapping)
        for item in mapping:
            item["ui_mapping"] = filter(lambda msg_class: (msg_class["msg_class"] == item["msg_class"] and msg_class["msg_type"]==item["msg_type"]) ,msg_class_mapping)[0]["ui_mapping"]
            item["id"] = self.generate_key(item["msg_class"],item["address"])
        return mapping

    def parse_file(self, file_path):
        json_object = json.load(file(file_path))
        return json_object

    def get_value_from_msg(self, jobj, json_path):
        # returns list
        return jsonpath.jsonpath(jobj, json_path, 'VALUE', False)

    def set_value_to_msg(self, jobj, json_path, value):
        path_array = jsonpath.jsonpath(jobj, json_path, 'IPATH', False)[0]

        # building expression jobj[el1][el2] = 123

        path_str = "jobj"
        for item in path_array:
            path_str = path_str + "['" + item + "']"
        var_type = type(value)
        if var_type is bool:
            path_str = path_str + " = " + str(value)
        elif var_type is int:
            path_str = path_str + " = " + str(value)
        elif var_type is float:
            path_str = path_str + " = " + str(value)
        elif var_type is str:
            path_str = path_str + " = '" + str(value) + "'"
        elif var_type is dict:
            path_str = path_str + " = " + json.dumps(value)
        else :
            log.error("!!!!UNKNOWN OBJECT TYPE , set operation will be skipped. Type is"+str(var_type)+" value "+str(value))
        exec (path_str)

    # params have to have the same values as explained in ui_mapping part of msg class mapping
    def generate_command_from_user_params(self,msg_key,params):
        msg_template = self.load_template_by_key(msg_key)
        msg_class_map = self.get_msg_class_by_key(msg_key)
        #parameters = {"value":"True"}
        for k,v in params.items():
            path = msg_class_map["ui_mapping"][k+"_path"]
            # converting to float if expected type is float
            if msg_class_map["ui_mapping"]["ui_element"]=="input_num_field":
                if msg_class_map["ui_mapping"]["num_type"]=="float":
                    v = float(v)
                else:
                    v = int(v)

            self.set_value_to_msg(msg_template,path,v)
        return msg_template

    def add_address_to_mapping(self,address,msg_class):
        # register new address
        log.info("Adding address to the mapping , address = "+str(address)+" msg_class="+str(msg_class))
        addr_map = self.load_address_mapping()
        addr_map.append({"msg_class":msg_class,"address":address,"name":msg_class,"msg_type":"event","group_name":"table1"})
        self.address_mapping = addr_map
        self.serialize_address_mapping()

    def remove_address_from_mapping(self,address,msg_class):
        log.info("Removing address from mapping , address = "+str(address)+" msg_class="+str(msg_class))
        # addr = filter(lambda addr_map: (addr_map["msg_class"] == msg_class and addr_map["address"]==address),self.address_mapping)
        i=0
        item_to_delete = -1
        for addr_map in self.address_mapping:
           if addr_map["msg_class"] == msg_class and addr_map["address"]==address:
               item_to_delete = i
           i=i+1
        if item_to_delete > -1:
            log.info("deleting item nr = "+str(item_to_delete))
            del self.address_mapping[item_to_delete]
        self.serialize_address_mapping()

    def serialize_address_mapping(self):
        log.info("Serializing address mapping to file "+self.address_mapping_file_path)
        f = open(self.address_mapping_file_path,"w")
        f.write(json.dumps(self.address_mapping,indent=True))
        f.close()



if __name__ == "__main__":

    m = MessageManager()
    m.app_root_path = "C:\ALWorks\SG\BlackflyTestSuite"
    print type({"test":1})
    flist = m.load_templates()
    jobj = m.parse_file(os.path.join(m.commands_dir, "include.json"))

    print m.get_value_from_msg(jobj, "$.command.name")[0]
    # m.set_value_to_msg(jobj, "$.command.name", "Test new path")
    # print jobj
    # print json.dumps(m.generate_linked_mapping(m.load_msg_class_mapping(),m.load_address_mapping()),indent=True)
    # print  m.load_template_by_key("temperature@.zw.15.multilevel_sensor.1.events")
    # print m.get_msg_class_by_key("temperature@.zw.15.multilevel_sensor.1.events")
    print json.dumps(m.generate_command_from_user_params("temperature@.zw.15.multilevel_sensor.1.events",{"value":"33","unit":"F"}) , indent=True)