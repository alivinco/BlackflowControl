from libs.iot_msg_lib.iot_msg import IotMsg, PayloadType, MsgType


class ServiceDiscovery:
    def __init__(self, sync_async_client , cache = dict()):
        self.sync_async_client = sync_async_client
        self.cache = cache
        self.cache["containers"] = None

    def discover(self , force_rediscover=False):
        if self.cache["containers"] and not force_rediscover:
            return self.cache["containers"]
        else:
            msg = IotMsg("blackflow", MsgType.CMD, "discovery", "find")
            r = self.sync_async_client.send_and_wait_aggregated_response(msg, "/discovery/commands", "/discovery/events", "discovery.report" ,2)
            result = list()
            for item in r :
                result.append(item.get_properties())
            self.cache["containers"] = result
            return result

    def get_containers(self):
        r = list()
        for item in self.discover():
            r.append(item["props"]["container_id"])
        return r




