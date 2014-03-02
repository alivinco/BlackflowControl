__author__ = 'aleksandrsl'
import os
import json
import jsonpath
import copy
# msg_list = {"events": ["file_name"], "commands": ["file_name"]}
msg_list = [{"file_name": "inclusion.json", "type": "event"}]


class MessageManager:
    def __init__(self):
        self.app_root_path = os.getcwd()
        self.events_dir = os.path.join(self.app_root_path, "messages", "events")
        self.commands_dir = os.path.join(self.app_root_path, "messages", "commands")
        self.msg_class_path_event = "$.event.type"
        self.msg_class_path_command = "$.command.name"
        self.msg_class_mapping = self.load_msg_class_mapping()
        self.address_mapping = self.load_address_mapping()

    def load_templates(self):

        msg_list = []
        for file in os.listdir(self.events_dir):
            msg_list.append({"file_name": file, "type": "event"})
        for file in os.listdir(self.commands_dir):
            msg_list.append({"file_name": file, "type": "command"})

        return msg_list
    def get_msg_class_by_key(self,msg_key):
        print msg_key
        split_str = msg_key.split("@")
        msg_class = split_str[0]
        address = split_str[1]

        if "event" in address: msg_type = "event"
        elif "commands" in address: msg_type = "command"
        else: msg_type = "unknown"

        return filter(lambda map_item: (map_item["msg_class"] == msg_class and map_item["msg_type"]==msg_type) ,self.msg_class_mapping)[0]

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
        jobj = json.load(file(os.path.join(self.app_root_path, "configs", "msg_class_mapping.json")))
        return jobj

    def load_address_mapping(self):
        jobj = json.load(file(os.path.join(self.app_root_path, "configs", "address_mapping.json")))
        return jobj

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

        path_str = "jobj"
        for item in path_array:
            path_str = path_str + "['" + item + "']"
        var_type = type(value)
        if var_type is bool:
            path_str = path_str + " = " + str(value)
        elif var_type is str:
            path_str = path_str + " = '" + str(value) + "'"
        elif var_type is dict:
            path_str = path_str + " = " + json.dumps(value)
        exec (path_str)

    # params have to have the same values as explained in ui_mapping part of msg class mapping
    def generate_command_from_user_params(self,msg_key,params):
        msg_template = self.load_template_by_key(msg_key)
        msg_class_map = self.get_msg_class_by_key(msg_key)
        #parameters = {"value":"True"}
        for k,v in params.items():
            path = msg_class_map["ui_mapping"][k+"_path"]
            print path
            self.set_value_to_msg(msg_template,path,v)
        return msg_template



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