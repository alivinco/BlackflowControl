from modules.msg_cache import MsgCache
from modules.msg_manager import MessageManager


__author__ = 'alivinco'
import json, os


class MsgPipeline():
    def __init__(self, msg_man,cache):
        self.msg_man = msg_man
        self.cache = cache
        #[{"type":"single","event_path":"$.event.type","command_path":"$.event.type","priority":1}]


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
        cache_key = ""
        addr_is_registered = self.__check_address(address)
        msg_class = self.__get_msg_class_from_msg(payload)
        if msg_class :
           msg_class_is_registered = self.__check_msg_class(msg_class)
           cache_key = self.msg_man.generate_key(msg_class,address)


        if addr_is_registered and msg_class_is_registered:
            # message is known and registered in system
            exdt = self.__extract_data(address,msg_class,payload)
            self.cache.put(cache_key,payload,exdt["ui_mapping"],exdt["extracted_values"])
            print "success"
            return {"success":True,"code":0}

        elif not addr_is_registered and msg_class and msg_class_is_registered :
            # the address is not known to system but message class is known
            # let's add the address to the mapping
            self.msg_man.add_address_to_mapping(address,msg_class)
            exdt = self.__extract_data(address,msg_class,payload)
            self.cache.put(cache_key,payload,exdt["ui_mapping"],exdt["extracted_values"])
            print "Address "+address+" doesn't exist in mapping file .It will be added automatically "
            return {"success":True,"code":1,"text":"New address has been registered :"+address}

        elif not addr_is_registered and msg_class and not msg_class_is_registered:
            # the address is not known to the system , msg class is not known to system but msg_class is not empy .
            # Means new unregistered command class
            # let's add into approve cache for user approval
            print "Unknown message class:"+msg_class+". It will be added for user approval"
            self.cache.put_msg_class_for_approval(address,payload,msg_class,"Message class is unknown and has to be approved")
            return {"success":True,"code":1,"text":"Unknown message class:"+msg_class+". It will be added for user approval"}

        elif not addr_is_registered and not msg_class :
            # the address is unknown and default message class path doesn't exists
            # check ignore list and then either make log entry or ignore
            print "Address :"+address+" is unknown and command class can't be extracted from the message.The message will be skipped"
            return {"success":False,"code":1,"text": "Address :"+address+" is unknown and command class can't be extracted from the message.The message will be skipped"}

        return {"success":False}

    def process_command(self,mqtt, address, payload ):
        # push message to cache
        # publish to mqtt
        msg_class = self.__get_msg_class_from_msg(payload)
        print "msg_class-"+str(msg_class)

        mqtt.mqtt.publish(address,json.dumps(payload),1)

        exdt = self.__extract_data(address,msg_class,payload)
        cache_key = self.msg_man.generate_key(msg_class,address)
        self.cache.put(cache_key,payload,exdt["ui_mapping"],exdt["extracted_values"])
        return {"success":True}

    def __get_msg_class_from_msg(self, payload):
        """
        The function trying to extract message class by given path
        :param payload:
        :return:
        """
        for path in self.msg_man.global_configs["msg_class_lookup_path"]:
           msg_class = self.msg_man.get_value_from_msg(payload, path["path"])
           if msg_class:
               return msg_class[0]
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



    def __extract_data(self,address,msg_class,payload):
         # extract values
        extracted_values = {}
        ui_mapping = {}
        id = self.msg_man.generate_key(msg_class,address)
        # print id
        try:
            ui_mapping = self.msg_man.get_msg_class_by_key(id)["ui_mapping"]
            for key,value in ui_mapping.items():
                if "path" in key:
                    print "trying to extract data from "+value
                    ex_value = self.msg_man.get_value_from_msg(payload,value)[0]
                    extracted_values[key.replace("_path","")]=ex_value
        except Exception as ex :
            #default value

            ui_mapping["ui_element"] = {"ui_element":"free_text","value_path":"$.event.value"}
            print "Can't extract ui mapping data"

        return {"ui_mapping":ui_mapping,"extracted_values":extracted_values}


if __name__ == "__main__":
    m = MessageManager()
    cache = MsgCache(m)
    t = MsgPipeline(m,cache)
    jobj = m.parse_file(os.path.join(m.events_dir, "inclusion.json"))
    t.process_event("/zw/inclusion",jobj)
    print cache.approve_cache