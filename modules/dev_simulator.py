from modules.msg_manager import MessageManager

__author__ = 'alivinco'
import os ,json

class DeviceSimulator:

    def __init__(self,msg_manager):

        self.msg_man = msg_manager
        self.flip_mapping = {"binary_light":"toggle_switch","sensor_value":"input_num_field","free_text":"json_input"}

    def get_msg_mapping(self):
        mapping = self.msg_man.generate_linked_mapping(self.msg_man.load_msg_class_mapping(), self.msg_man.load_address_mapping())
        # we need only events
        r = filter(lambda addr: (addr["msg_type"] == "event"),mapping)
        # flip ui elements
        self.__flip_event_to_command_ui_control(r)
        return r

    def __flip_event_to_command_ui_control(self,address_mapping):

        for item in address_mapping:
           print item
           event_ui = str(item["ui_mapping"]["ui_element"])
           print item["ui_mapping"]["ui_element"]
           item["ui_mapping"]["ui_element"] = str(self.flip_mapping[event_ui])


           print "next item"

if __name__ == "__main__":
    m = MessageManager()
    t = DeviceSimulator(m)
    print json.dumps(t.get_msg_mapping(),indent=True)
