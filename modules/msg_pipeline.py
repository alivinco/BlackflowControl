import uuid
import time
from modules.msg_cache import MsgCache
from modules.msg_manager import MessageManager


__author__ = 'alivinco'
import json, os
import configs.log
import logging,logging.config
logging.config.dictConfig(configs.log.config)
log = logging.getLogger("bf_msg_pipeline")


class MsgPipeline():
    def __init__(self, msg_man,cache,timeseries=None):
        self.msg_man = msg_man
        self.cache = cache
        self.timeseries = timeseries
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

        # mqtt broker system message
        if "$SYS" in address :
            self.cache.put_generic(address,payload)
            return {"success":True,"code":0}

        log.info("New event is entering message processing pipeline")
        msg_class_is_registered = False
        cache_key = ""
        addr_is_registered = self.__check_address(address)
        msg_class = self.__get_msg_class_from_msg(payload)
        if msg_class :
           msg_class_is_registered = self.__check_msg_class(msg_class)
           cache_key = self.msg_man.generate_key(msg_class,address)
        else :
           log.error("The system can't identify message class . Therefore message processing stoped and the message will be skipped.")
           log.debug( json.dumps(payload,indent=True))

        if addr_is_registered and msg_class_is_registered:
            # message is known and registered in system
            exdt = self.__extract_data(address,msg_class,payload)
            self.__update_timeseries(exdt)
            self.cache.put(cache_key,payload,exdt["ui_mapping"],exdt["extracted_values"])
            log.info("Message class = "+msg_class+" and address = "+address+" are known to the system")
            return {"success":True,"code":0}

        # elif (not addr_is_registered and msg_class_is_registered) or (addr_is_registered and msg_class and not msg_class_is_registered) :
        elif (not addr_is_registered and msg_class_is_registered) :
            # the address is not known to the system but message class is known OR
            # the address is know but msg_class is not know to the system , for example when the same address can produce several events like error report and temperature readings
            # let's add the address to the mapping
            self.msg_man.add_address_to_mapping(address,msg_class)
            exdt = self.__extract_data(address,msg_class,payload)
            self.__update_timeseries(exdt)
            self.cache.put(cache_key,payload,exdt["ui_mapping"],exdt["extracted_values"])
            log.info("Address "+address+" or message class doesn't exist in mapping file .It will be added automatically ")
            return {"success":True,"code":1,"text":"New address has been registered :"+address}

        elif msg_class and not msg_class_is_registered:
            # the address is not known to the system , msg class is not known to system but msg_class is not empy .
            # Means new unregistered command class
            # let's add into approve cache for user approval
            log.info("Unknown message class:"+msg_class+". It will be added for user approval")
            self.cache.put_msg_class_for_approval(address,payload,msg_class,"Message class is unknown and has to be approved")
            return {"success":True,"code":1,"text":"Unknown message class:"+msg_class+". It will be added for user approval"}

        elif not addr_is_registered and not msg_class :
            # the address is unknown and default message class path doesn't exists
            # check ignore list and then either make log entry or ignore
            log.info("Address :"+address+" is unknown and command class can't be extracted from the message.The message will be skipped")
            return {"success":False,"code":1,"text": "Address :"+address+" is unknown and command class can't be extracted from the message.The message will be skipped"}
        else :
            log.info("The message doesn't match any of rules and will be skipped.")
            log.debug(json.dumps(payload,indent=True))

        return {"success":False}

    def process_command(self,mqtt, address, payload ):
        # push message to cache
        # publish to mqtt
        log.info("New command entered message pipeline")
        msg_class = self.__get_msg_class_from_msg(payload)
        log.info("Msg class = "+str(msg_class))
        self.__update_static_part_of_message(payload,address)
        mqtt.publish(address,json.dumps(payload),1)

        exdt = self.__extract_data(address,msg_class,payload)
        cache_key = self.msg_man.generate_key(msg_class,address)
        self.cache.put(cache_key,payload,exdt["ui_mapping"],exdt["extracted_values"])
        log.info("Message was saved to cache with key ="+str(cache_key))
        return {"success":True}

    def __get_msg_class_from_msg(self, payload):
        """
        The function trying to extract message class by given path
        :param payload:
        :return:
        """
        for path in self.msg_man.global_configs["msg_class_lookup_path"]:
           try:
               if path["type"]=="single":
                   msg_class = self.msg_man.get_value_from_msg(payload, path["path"])
                   if msg_class:
                      return msg_class[0]
               elif path["type"]=="multiple":
                   # message class can be aggregated from several field
                   # all results are concatenated with "." , for example meter.power
                   class_list = []
                   for item in path["path"]:
                     t = self.msg_man.get_value_from_msg(payload,item)
                     if t :
                       class_list.append(t[0])
                   if len(class_list)>0:
                       msg_class = ".".join(class_list)
                       return msg_class

           except Exception as ex:
               log.debug("__get_msg_class_from_msg : class can't be extracted from msg because of error :"+str(ex))

        return None

    def __update_static_part_of_message(self,payload,topic = "/dev/default"):
        payload["origin"]["@type"]="app"
        payload["origin"]["@id"]="blackfly"
        payload["origin"]["vendor"]="blackfly"
        payload["origin"]["location"]="lab"
        if "command" in payload: payload["command"]["target"] = topic
        payload["uuid"] = str(uuid.uuid4())
        payload["creation_time"] = int(time.time()) * 1000


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
        """
         Method extracts simple data from message . The date then is stored in cache in is used by UI to render element value .
        :param address:
        :param msg_class:
        :param payload:
        :return:
        """
        extracted_values = {}
        ui_mapping = {}
        key = self.msg_man.generate_key(msg_class,address)
        address_map = self.msg_man.get_address_by_key(key)
        # print id
        try:
            ui_mapping = self.msg_man.get_msg_class_by_key(key)["ui_mapping"]
            override_path = ""
            if "override_value_path" in address_map:
               override_path = address_map["override_value_path"]
               if override_path :
                  log.debug("Extracting data from overrided path = "+str(override_path))
                  ex_value = self.msg_man.get_value_from_msg(payload,override_path)[0]
                  log.debug("Extracted data is = "+str(ex_value))
                  extracted_values["value"] = ex_value

            if not override_path :
                for key,value in ui_mapping.items():
                    if "path" in key:
                        log.debug("Extracting data from = "+str(value))
                        ex_value = self.msg_man.get_value_from_msg(payload,value)[0]
                        log.debug("Extracted data is = "+str(ex_value))
                        extracted_values[key.replace("_path","")]=ex_value
            extracted_values["dev_id"] = address_map["id"]
        except Exception as ex :
            #default value
            ui_mapping["ui_element"] = {"ui_element":"free_text","value_path":"$.event.value"}
            log.error("Can't extract ui mapping data")
            log.exception(ex)

        return {"ui_mapping":ui_mapping,"extracted_values":extracted_values}

    def __update_timeseries(self,exdt):
       try:
         value = exdt["extracted_values"]["value"]
         if isinstance(value,(int,float,bool)):
            if isinstance(value,bool): value = int(value)
            self.timeseries.insert(exdt["extracted_values"]["dev_id"],value,2)
         else:
            log.debug("Value is not a number , therefore will be skipped")
       except Exception as ex :
           log.debug(ex)


if __name__ == "__main__":
    m = MessageManager()
    cache = MsgCache(m)
    t = MsgPipeline(m,cache)
    jobj = m.parse_file(os.path.join(m.events_dir, "meter.power.json"))
    # msg_clas = t.get_msg_class_from_msg(jobj)
    # print msg_clas
    # t.process_event("/zw/inclusion",jobj)
    # print cache.approve_cache