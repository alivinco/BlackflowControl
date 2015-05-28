from shutil import copyfile
from libs.simple_jsonpath import SimpleJsonPath

__author__ = 'aleksandrsl'
import os
import json
import copy
import logging
# import logging.config
from libs import jsonpath
# import configs.log


# logging.config.dictConfig(configs.log.config)
log = logging.getLogger("bf_msg_manager")

# msg_list = {"events": ["file_name"], "commands": ["file_name"]}
msg_list = [{"file_name": "inclusion.json", "type": "event"}]


class MessageManager:
    def __init__(self):
        self.app_root_path = os.getcwd()
        self.events_dir = os.path.join(self.app_root_path, "messages", "events")
        self.commands_dir = os.path.join(self.app_root_path, "messages", "commands")
        self.msg_class_mapping_file_path = os.path.join(self.app_root_path, "configs", "msg_class_mapping.json")
        self.address_mapping_file_path = os.path.join(self.app_root_path, "configs", "address_mapping.json")
        self.services_to_msg_mapping_file_path = os.path.join(self.app_root_path, "configs", "services_to_msg_mapping.json")
        self.msg_class_mapping = self.load_msg_class_mapping()
        self.address_mapping = self.load_address_mapping()
        self.services_to_msg_mapping = self.load_service_to_msg_mapping()

        self.global_configs_path = os.path.join(self.app_root_path, "configs", "global.json")
        self.global_configs = json.load(file(self.global_configs_path))
        self.ui_elements_command = ["input_num_field","toggle_switch"]
        self.ui_elements_event = ["binary_light","sensor_value","free_text"]
        self.jsonpath = SimpleJsonPath()


    def load_templates(self):

        msg_list = []
        for file in os.listdir(self.events_dir):
            msg_list.append({"file_name": file, "type": "event"})
        for file in os.listdir(self.commands_dir):
            msg_list.append({"file_name": file, "type": "command"})

        return msg_list

    def get_msg_class_template_by_name(self, msg_type, msg_class_name):

        if "event" == msg_type:
            result = json.load(file(os.path.join(self.app_root_path, "messages", "events", msg_class_name + ".json")))
        elif "command" == msg_type:
            result = json.load(file(os.path.join(self.app_root_path, "messages", "commands", msg_class_name + ".json")))
        else:
            result = None

        return result

    def save_template(self,msg_type,msg_class_name,payload):
        path = os.path.join(self.app_root_path, "messages", msg_type+"s", msg_class_name + ".json")
        f = open(path,"w")
        f.write(payload)
        f.close()
        log.info("New template was saved to file = "+path)

    def get_msg_clas_by_name(self, msg_type, msg_class_name):
        return filter(lambda map_item: (map_item["msg_class"] == msg_class_name and map_item["msg_type"] == msg_type),
                      self.msg_class_mapping)[0]

    def get_msg_class_by_key(self, msg_key):
        split_str = msg_key.split("@")
        msg_class = split_str[0]
        address = split_str[1]

        if "event" in address:
            msg_type = "event"
        elif "commands" in address:
            msg_type = "command"
        else:
            log.info("the system can't identify message type , default value 'event' will be set")
            msg_type = "event"

        return filter(lambda map_item: (map_item["msg_class"] == msg_class and map_item["msg_type"] == msg_type),
                      self.msg_class_mapping)[0]

    def add_msg_class(self, msg_class, msg_type, ui_element=None, value_path=None):

        #define default values
        default_path = ""
        if msg_type == "command":
            default_path = self.global_configs["defaults"]["cmd_value_path_for_new_class"]
        elif msg_type == "event":
            default_path = self.global_configs["defaults"]["event_value_path_for_new_class"]

        new_class = {"msg_class": msg_class, "msg_type": msg_type,
                     "ui_mapping": {"ui_element": "free_text", "value_path": default_path}}

        self.msg_class_mapping.append(new_class)
        # let's serialize the updated structure
        # f = open(self.msg_class_mapping_file_path,"w")
        json.dump(self.msg_class_mapping, open(self.msg_class_mapping_file_path, "w"), indent=True)

    def load_template_by_key(self, msg_key):
        msg_class = msg_key.split("@")[0]
        address = msg_key.split("@")[1]
        result = None
        if "event" in address:
            result = json.load(file(os.path.join(self.app_root_path, "messages", "events", msg_class + ".json")))
        elif "command" in address:
            result = json.load(file(os.path.join(self.app_root_path, "messages", "commands", msg_class + ".json")))
        else:
            result = None
        return result

    def load_msg_class_mapping(self):
        log.debug("Loading msg class mapping.")
        jobj = json.load(file(self.msg_class_mapping_file_path))
        return jobj

    def load_service_to_msg_mapping(self):
        log.debug("Loading service to msg mapping.")
        jobj = json.load(file(self.services_to_msg_mapping_file_path))
        return jobj

    def load_address_mapping(self):
        log.debug("Loading address mapping.")
        jobj = json.load(file(self.address_mapping_file_path))
        # let's add a key
        for map in jobj:
            map["key"] = self.generate_key(map["msg_class"], map["address"])
        return jobj

    def reload_all_mappings(self):
        self.msg_class_mapping = self.load_msg_class_mapping()
        self.address_mapping = self.load_address_mapping()
        self.load_service_to_msg_mapping()

    def generate_key(self, msg_class, address):
        return msg_class + "@" + address.replace("/", ".")

    def decode_key(self, msg_key):
        msg_class = msg_key.split("@")[0]
        address = msg_key.split("@")[1]
        address = address.replace(".", "/")
        return {"msg_class": msg_class, "address": address}

    def generate_linked_mapping(self, msg_class_mapping, address_mapping):
        mapping = copy.copy(address_mapping)
        result = []
        for item in mapping:
            mclass = filter(lambda msg_class: ( msg_class["msg_class"] == item["msg_class"] and msg_class["msg_type"] == item["msg_type"]),msg_class_mapping)
            if len(mclass)>0:
               item["ui_mapping"] = mclass[0]["ui_mapping"]
               # item["id"] = self.generate_key(item["msg_class"], item["address"])

               result.append(item)
            else :
               log.error("Linked mapping can't be generated because class = "+item["msg_class"]+" does not exist in msg class mapping.")

        return result

    def parse_file(self, file_path):
        json_object = json.load(file(file_path))
        return json_object

    def get_value_from_msg(self, jobj, json_path):
        # returns list
        # return jsonpath.jsonpath(jobj, json_path, 'VALUE', False)
        return self.jsonpath.get(jobj,json_path)

    def set_value_to_msg(self, jobj, json_path, value):
        log.debug("JsonPath to set the value :"+str(json_path))
        path_array = jsonpath.jsonpath(jobj, json_path, 'PATH',0, False)[0]

        # building expression jobj[el1][el2] = 123

        path_str = "jobj"
        path_str = path_array.replace("$","jobj")
        # print path_array
        # for item in path_array:
        #     if item is int :
        #         path_str = path_str + "[" + str(item) + "]"
        #     else :
        #         path_str = path_str + "['" + str(item) + "']"
        var_type = type(value)
        if var_type is bool:
            path_str = path_str + " = " + str(value)
        elif var_type is int:
            path_str = path_str + " = " + str(value)
        elif var_type is float:
            path_str = path_str + " = " + str(value)
        elif var_type is str:
            path_str = path_str + " = '" + str(value) + "'"
        elif var_type is unicode:
            path_str = path_str + " = '" + str(value) + "'"
        elif var_type is dict:
            path_str = path_str + " = " + json.dumps(value)
        else:
            log.error(
                "!!!!UNKNOWN OBJECT TYPE , set operation will be skipped. Type is" + str(var_type) + " value " + str(
                    value))
        log.debug("Generated expression "+str(path_str))

        exec (path_str)

    # params have to have the same values as explained in ui_mapping part of msg class mapping
    #
    def generate_command_from_user_params(self, msg_key, params):
        msg_template = self.load_template_by_key(msg_key)
        msg_class_map = self.get_msg_class_by_key(msg_key)
        address = self.get_address_by_key(msg_key)
        #parameters = {"value":"True"}
        for k, v in params.items():
            if "properties_are_key_value" in msg_class_map["ui_mapping"] :
                if k == "prop_key":
                   if "prop_int_value" in params:
                     value =int(params["prop_int_value"])
                   elif k == "prop_float_value":
                     value =int(params["prop_float_value"])
                   else :
                     value = params["prop_str_value"]

                   msg_template["command"]["properties"][v] = {"value":value}
            else :
                if "override_properties" in address:
                  if address["override_properties"]:
                    log.debug("The system overriding properties from template by properties from address mapping.")
                    msg_template["command"]["properties"] = address["override_properties"]

                  if address["override_value_path"]:
                    path = address["override_value_path"]
                    log.debug("The system overriding value path by "+str(path))
                  else :
                    path = msg_class_map["ui_mapping"][k + "_path"]
                else :
                    path = msg_class_map["ui_mapping"][k + "_path"]
                if "num_input" in k:
                    v = int(v)

                # converting to float if expected type is float
                if msg_class_map["ui_mapping"]["ui_element"] == "input_num_field" or msg_class_map["ui_mapping"]["ui_element"] == "slider" :
                    if msg_class_map["ui_mapping"]["num_type"] == "float":
                        v = float(v)
                    else:
                        v = int(v)
                self.set_value_to_msg(msg_template, path, v)
        return msg_template

    def update_address_mapping(self, key, name, msg_class, msg_type, address,override_properties="",override_value_path="",record_history=False,serialize=True):
        if key:
            item = filter(lambda addr: (addr["key"] == key ), self.address_mapping)[0]
            item["msg_class"] = msg_class
            item["address"] = address
            item["name"] = name
            item["msg_type"] = msg_type
            item["override_properties"]=override_properties
            item["override_value_path"]=override_value_path
            item["record_history"] = record_history
            log.info("Address mapping updated with " + str(item))
        else :
            new_id = self.get_new_addr_id()
            self.address_mapping.append({"id":new_id,"msg_class": msg_class, "address": address, "name": name, "msg_type": msg_type,"record_history":record_history, "override_properties":override_properties,"override_value_path":override_value_path,"key": self.generate_key(msg_class, address)})

        if serialize :self.serialize_address_mapping()


    def add_address_to_mapping(self, address, msg_class,serialize=True):
        # register new address
        # calculating new id
        # self.address_mapping
        log.info("Adding address to the mapping , address = " + str(address) + " msg_class=" + str(msg_class))
        # addr_map = self.address_mapping
        if not self.check_if_address_exists(address,msg_class):
            new_id = self.get_new_addr_id()
            if "event" in address :
                self.address_mapping.append({"id":new_id,"msg_class": msg_class, "address": address, "name": msg_class, "msg_type": "event","record_history":False, "group_name": "","override_properties":"","override_value_path":"","key": self.generate_key(msg_class, address)})
            elif "command" in address :
                self.address_mapping.append({"id":new_id,"msg_class": msg_class, "address": address, "name": msg_class, "msg_type": "command", "group_name": "","record_history":False,"override_properties":"","override_value_path":"","key": self.generate_key(msg_class, address)})
            # self.address_mapping = addr_map
            if serialize: self.serialize_address_mapping()
        else :
            log.info("The address is already registered and therefore ADD operation will be skipped.")

    def check_if_address_exists(self,address,msg_class):
        r = filter(lambda addr: (addr["msg_class"] == msg_class and addr["address"] == address ),self.address_mapping)
        if len(r)>0:
            return True
        else :
            return False

    def get_new_addr_id(self):
        new_id = sorted(self.address_mapping,key = lambda item:item["id"])[-1]["id"]+1
        log.info("New address id is = "+str(new_id))
        return new_id

    def get_address_by_key(self, key):
        try:
          k = self.decode_key(key)
          r = filter(lambda addr: (addr["msg_class"] == k["msg_class"] and addr["address"] == k['address']),self.address_mapping)[0]
        except Exception as ex :
          r = None
        return r

    def get_address_map(self,msg_class,address):
        try:
          r = filter(lambda addr: (addr["msg_class"] == msg_class and addr["address"] == address ),self.address_mapping)[0]
        except Exception as ex :
          r = None
        return r

    def remove_address_from_mapping(self, id):
        log.info("Removing address from mapping , id ="+str(id))
        # addr = filter(lambda addr_map: (addr_map["msg_class"] == msg_class and addr_map["address"]==address),self.address_mapping)
        i = 0
        item_to_delete = -1
        for addr_map in self.address_mapping:
            if addr_map["id"] == id :
                item_to_delete = i
            i = i + 1
        if item_to_delete > -1:
            log.info("deleting item nr = " + str(item_to_delete))
            del self.address_mapping[item_to_delete]
        self.serialize_address_mapping()

    def bulk_address_removal(self,search_str):
        removed_ids = []
        r_address_mapping = []
        log.info("Bulk address removal . All devices which contains "+search_str+" in it's address will be removed from the system")
        for item in self.address_mapping:
            if not(search_str in item["address"]):
                r_address_mapping.append(item)
            else :
                removed_ids.append(item["id"])
                log.info("Removing device with address = "+item["address"]+" id = "+str(item["id"]))

        self.address_mapping = copy.deepcopy(r_address_mapping)
        self.serialize_address_mapping()
        return removed_ids

    def find_replace_address(self,find,replace_to):
        """
         The method loops over all adresses and replaces "find" part with "replace" part
         "key": "binary.switch@.dev.zw.2.bin_switch.1.commands",
         "address": "/dev/zw/2/bin_switch/1/commands",
        """

        for item in self.address_mapping:

            if find in item["address"]:
                log.info("Updating "+item["address"]+" ."+find+" will be replaced by "+replace_to)
                item["address"] = item["address"].replace(find,replace_to)
                d_key = self.decode_key(item["key"])
                d_key["address"]= d_key["address"].replace(find,replace_to)
                item["key"] = self.generate_key(d_key["msg_class"],d_key["address"])
                log.debug("New key "+item["key"])

        self.serialize_address_mapping()

    def generate_address_mappings_for_services(self,list_of_services,device_name=""):
        """
        :param list_of_services: list_of_services - is list of service where each service is in a form of :
        {"Control":True,"Support":True,"Uri":"/dev/zw/4/dev_sys/1","Type":"dev_sys"}
        """
        for service in list_of_services:
            if service["Type"] in self.services_to_msg_mapping:
                service_map = self.services_to_msg_mapping[service["Type"]]

                for event_msg_class in service_map["events"]:
                    address = service["Uri"]+"/events"
                    if device_name :name = device_name+"=>"+event_msg_class
                    else : name = event_msg_class
                    if not self.check_if_address_exists(address,event_msg_class):
                        self.update_address_mapping(None, name, event_msg_class,"event", address,serialize=False)
                for command_msg_class in service_map["commands"]:
                    address = service["Uri"]+"/commands"
                    if device_name :name = device_name+"=>"+command_msg_class
                    else : name = event_msg_class
                    if not self.check_if_address_exists(address,command_msg_class):
                        self.update_address_mapping(None, name, command_msg_class,"command", address,serialize=False)
            else :
                log.warn("Service of type = %s doesn't have a mapping therefore will be skipped "%service["Type"])

        self.serialize_address_mapping()


    def serialize_address_mapping(self):
        log.info("Serializing address mapping to file " + self.address_mapping_file_path)
        f = open(self.address_mapping_file_path, "w")
        f.write(json.dumps(self.address_mapping, indent=True))
        f.close()

    def serialize_class_mapping(self):
        log.info("Serializing class mapping to file " + self.msg_class_mapping_file_path)
        f = open(self.msg_class_mapping_file_path, "w")
        f.write(json.dumps(self.msg_class_mapping, indent=True))
        f.close()

    def serialize_global_config(self):
        log.info("Serializing global config to " + self.global_configs_path)
        f = open(self.global_configs_path,"w")
        f.write(json.dumps(self.global_configs,indent=True))
        f.close()

    def reset_address_mapping(self):
        """
        The method does address_mapping reset by copying default file from scripts/config/address_mapping.json

        """
        default_mapping = os.path.join(self.app_root_path, "scripts","configs", "address_mapping.json")
        copyfile(default_mapping,self.address_mapping_file_path)
        self.reload_all_mappings()


if __name__ == "__main__":
    m = MessageManager()
    # m.app_root_path = "C:\ALWorks\SG\BlackflyTestSuite"
    # flist = m.load_templates()
    jobj = m.parse_file(os.path.join(m.commands_dir, "association.set.json"))

    # print m.get_value_from_msg(jobj, "$.command.properties.devices.value[0]")[0]
    # m.set_value_to_msg(jobj,"$.command.properties.devices.value[0]",3)
    print m.bulk_address_removal("s-455/dev/zw/26")
    # m.set_value_to_msg(jobj, "$.command.name", "Test new path")
    # print jobj
    # print json.dumps(m.generate_linked_mapping(m.load_msg_class_mapping(),m.load_address_mapping()),indent=True)
    # print  m.load_template_by_key("temperature@.zw.15.multilevel_sensor.1.events")
    # print m.get_msg_class_by_key("temperature@.zw.15.multilevel_sensor.1.events")
    # print json.dumps(m.generate_command_from_user_params("temperature@.zw.15.multilevel_sensor.1.events",{"value": "33", "unit": "F"}), indent=True)