import json
import os
import uuid
import time

__author__ = 'alivinco'

class Core():

    def __init__(self,type="NA",id="NA",vendor="NA",location="NA"):
        self.app_root_path = os.getcwd()
        self.origin={"@type":type,"@id":id,"vendor":vendor,"location":location}

    def get_message(self,msg_type,msg_class):
        msg = self.load_template(msg_type,msg_class)
        msg = self.__update_static_part_of_message(msg)
        return msg

    def load_template(self, msg_type,msg_class):
        """
        Method loads message template
        :param msg_type: command or event
        :param msg_class: for example binary.switch
        :return: message template as python object
        """

        result = None
        if "event" == msg_type:
            result = json.load(file(os.path.join(self.app_root_path, "messages", "events", msg_class + ".json")))
        elif "command" == msg_type:
            result = json.load(file(os.path.join(self.app_root_path, "messages", "commands", msg_class + ".json")))
        else:
            result = None
        return result

    def __update_static_part_of_message(self,payload):
        payload["origin"] = self.origin
        payload["uuid"] = str(uuid.uuid4())
        payload["creation_time"] = int(time.time()) * 1000

        if "command" in payload:
            payload["command"]["target"] = ""
        return payload

        # if "event" in payload:
        #     # /dev/zw/5/sen_temp/1/events
        #     t = topic.split("/")
        #     if t[1]=="dev":
        #         payload["origin"]["@id"]=t[3]
        #         payload["origin"]["@type"]=t[4]
        #         payload["origin"]["endp_id"]=t[5]


if __name__ == "__main__":
    c = Core()
    c.set_origin("app","blackfly","office")
    print c.get_message("command","config.set")
