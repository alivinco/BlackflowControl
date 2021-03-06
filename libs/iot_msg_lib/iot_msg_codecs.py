#     # Fisrt version of IOT JSON message format
#     JSON_IOT_MSG_V0 = 0
#     # Current version of IOT JSON message format
#     JSON_IOT_MSG_V1 = 1
#     # Binary encoded IOT message format
#     BINARY_IOT_MSG_V1 = 3
import datetime ,time

from iot_msg import MsgType, IotMsg

__author__ = 'alivinco'


class IotMsgCodec:
    @classmethod
    def get_msg_type(cls, type_str):
        inv_map = {v: k for k, v in cls.msg_type_to_string_map.items()}
        return inv_map[type_str]


class IotMsgToJsonIotMsgV0Codec(IotMsgCodec):
    msg_type_to_string_map = {
        MsgType.CMD: "command",
        MsgType.EVT: "event",
        MsgType.GET: "get"
    }

    @classmethod
    def encode(cls, iot_msg):
        r = {"origin": {"@id": iot_msg.origin, "@type": "app"},
             "uuid": iot_msg.uuid,
             "creation_time": int(time.time()),
             cls.msg_type_to_string_map[iot_msg.msg_type]: {"default": iot_msg.default, "subtype": iot_msg.msg_subclass, "@type": iot_msg.msg_class,
                                                            "properties": iot_msg.properties},
             "id": ""
             }
        if iot_msg.corid:
            r["corid"] = iot_msg.corid
        return r

    @classmethod
    def decode(cls, dict_msg):
        origin = dict_msg["origin"]["@id"] if "@id" in dict_msg else None
        if "command" in dict_msg:
            msg_type_str = "command"
        elif "event" in dict_msg:
            msg_type_str = "event"
        elif "get" in dict_msg:
            msg_type_str = "get"
        else:
            msg_type_str = ""
        imsg = IotMsg(origin, msg_type=cls.get_msg_type(msg_type_str), msg_class=dict_msg[msg_type_str]["@type"], msg_subclass=dict_msg[msg_type_str]["subtype"])
        if "corid" in dict_msg:
            imsg.corid = dict_msg["corid"]
        imsg.default = dict_msg[msg_type_str]["default"]
        if "properties" in dict_msg[msg_type_str]:
            imsg.set_properties(dict_msg[msg_type_str]["properties"])
        imsg.uuid = dict_msg["uuid"]
        return imsg


class IotMsgToJsonIotMsgV1Codec(IotMsgCodec):
    msg_type_to_string_map = {
        MsgType.CMD: "cmd",
        MsgType.EVT: "evt",
        MsgType.GET: "get"
    }

    @classmethod
    def encode(cls, iot_msg):
        r = {"type": cls.msg_type_to_string_map[iot_msg.msg_type],
                "cls": iot_msg.msg_class,
                "subcls": iot_msg.msg_subclass,
                "def": iot_msg.default,
                "props": iot_msg.properties,
                "uuid": iot_msg.uuid,
                "ctime": datetime.datetime.now().isoformat(),
                "ver": 1.0
                }
        if iot_msg.corid:
            r["corid"] = iot_msg.corid
        return r

    @classmethod
    def decode(cls, dict_msg):
        imsg = IotMsg(None, msg_type=cls.get_msg_type(dict_msg["type"]), msg_class=dict_msg["cls"], msg_subclass=dict_msg["subcls"])
        imsg.default = dict_msg["def"]
        imsg.set_properties(dict_msg["props"])
        imsg.uuid = dict_msg["uuid"]
        imsg.timestamp = dict_msg["ctime"]
        if "corid" in dict_msg:
            imsg.corid = dict_msg["corid"]
        return imsg


class IotMsgToBinaryIotMsgV1MsgCodec:
    @staticmethod
    def encode(IotMsg):
        pass

    @staticmethod
    def decode(IotMsg):
        pass
