__author__ = 'aleksandrsl'
import os
import json
import jsonpath
import copy
# msg_list = {"events": ["file_name"], "commands": ["file_name"]}
msg_list = [{"file_name": "inclusion.json", "type": "event"}]


class MessageManager:
    def __init__(self):
        self.root = "C:\ALWorks\SG\BlackflyTestSuite"
        self.events_dir = os.path.join(self.root, "messages", "events")
        self.commands_dir = os.path.join(self.root, "messages", "commands")
        self.msg_class_path_event = "$.event.type"
        self.msg_class_path_command = "$.command.name"

    def load_templates(self):

        msg_list = []
        for file in os.listdir(self.events_dir):
            msg_list.append({"file_name": file, "type": "event"})
        for file in os.listdir(self.commands_dir):
            msg_list.append({"file_name": file, "type": "command"})

        return msg_list

    def load_msg_class_mapping(self):
        jobj = json.load(file(os.path.join(self.root, "configs", "msg_class_mapping.json")))
        return jobj

    def load_address_mapping(self):
        jobj = json.load(file(os.path.join(self.root, "configs", "address_mapping.json")))
        return jobj

    def generate_id(self,msg_class,address):
        return msg_class+"@"+address.replace("/",".")

    def generate_linked_mapping(self,msg_class_mapping,address_mapping):
        mapping = copy.copy(address_mapping)
        for item in mapping:
            item["ui_mapping"] = filter(lambda msg_class: (msg_class["msg_class"] == item["msg_class"] and msg_class["msg_type"]==item["msg_type"]) ,msg_class_mapping)[0]["ui_mapping"]
            item["id"] = self.generate_id(item["msg_class"],item["address"])
        return mapping

    def parse_file(self, file_path):
        json_object = json.load(file(file_path))
        return json_object

    def get_value_from_msg(self, jobj, json_path):
        return jsonpath.jsonpath(jobj, json_path, 'VALUE', False)

    def set_value_to_msg(self, jobj, json_path, value):
        path_array = jsonpath.jsonpath(jobj, json_path, 'IPATH', False)[0]
        path_str = "jobj"
        for item in path_array:
            path_str = path_str + "['" + item + "']"
        path_str = path_str + " = '" + value + "'"
        exec (path_str)


if __name__ == "__main__":
    m = MessageManager()
    flist = m.load_templates()
    jobj = m.parse_file(os.path.join(m.commands_dir, "include.json"))

    print m.get_value_from_msg(jobj, "$.command.name")[0]
    m.set_value_to_msg(jobj, "$.command.name", "Test new path")
    print jobj
    print json.dumps(m.generate_linked_mapping(m.load_msg_class_mapping(),m.load_address_mapping()),indent=True)
