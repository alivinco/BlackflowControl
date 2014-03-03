__author__ = 'alivinco'
import json, os


class MsgPipeline():
    def __init__(self, mqtt, msg_man):
        self.mqtt = mqtt
        self.msg_man = msg_man
        #[{"type":"single","event_path":"$.event.type","command_path":"$.event.type","priority":1}]
        self.msg_class_path_list = json.loads(file(os.path.join(self.msg_man.app_root_path), "configs", "global.json"))

    def process_event(self, address, payload):
        # validate message if that belongs to any of known msg_classes and address mapping
        # if belongs then put to cache .
        # if message fail to validate :
        # if message belongs to known class but not found in address mapping
        # then add to mapping  and notify user
        # if message doesn't belong to any know class then :
        # than try to look up known path
        #      try to check message elements against message class list
        # notify user
        # if known pass exist , then ask user if the message class is correct then
        # add class and address into mapping
        # user can enter path manually and retry validation
        # if everything fails then add message to error_cache
        msg_class_is_registered = False
        addr_is_registered = self.__check_address(address)
        msg_class = self.__get_msg_class_from_msg(payload)
        if msg_class :
           msg_class_is_registered = self.__check_msg_class(msg_class)


        if addr_is_registered and msg_class_is_registered:
            # message is known and registered in system
            self.cache.put(address,payload)
            return {"success":True,"code":0}

        elif not addr_is_registered and msg_class and msg_class_is_registered :
            # the address is not known to system but message class is known
            # let's add the address to the mapping
            self.msg_man.add_address_to_mapping(address,msg_class)
            self.cache.put(address,payload)
            return {"success":True,"code":1,"text":"New address has been registered :"+address}

        elif not addr_is_registered and msg_class and not msg_class_is_registered:
            # the address is not known to system , msg class is not known to system but msg_class is not empy .
            # Means new unregistered command class
            # let's add to approve list
            pass

    def process_command(self, address, msg):
        # push message to cache
        # publish to mqtt
        pass

    def __get_msg_class_from_msg(self, payload):
        """
        The function trying to extract message class by given path
        :param payload:
        :return:
        """
        for path in self.msg_class_path_list:
            msg_class = self.msg_man.get_value_from_msg(payload, path)[0]
            if msg_class: return msg_class
        return None

    def __check_address(self, address):
        r = filter(lambda map_item: (map_item["address"] == address ), self.msg_man.address_mapping)
        if len(r) > 0:
            return True
        else:
            return False

    def __check_msg_class(self,msg_class):
        r = filter(lambda map_item: (map_item["msg_class"] == msg_class ), self.msg_man.msg_class_mapping)
        if len(r) > 0:
            return True
        else:
            return False


