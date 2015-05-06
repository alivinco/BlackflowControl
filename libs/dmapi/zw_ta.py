from libs.dmapi.core import Core

__author__ = 'alivinco'

class ZwTa(Core):
    def get_routing_info(self):
        return self.get_message("command","zw_ta.get_routing_info")

    def get_node_info(self,node_id):
        msg = self.get_message("command","zw_ta.get_node_info")
        msg["command"]["default"]["value"]=node_id
        return msg

    def inclusion_mode(self,start=True):
        msg = self.get_message("command","zw_ta.inclusion_mode")
        msg["command"]["default"]["value"]=start
        return msg

    def exclusion_mode(self,start=True):
        msg = self.get_message("command","zw_ta.exclusion_mode")
        msg["command"]["default"]["value"]=start
        return msg

    def remove_failed_node(self,node_id):
        msg = self.get_message("command","zw_ta.remove_failed_node")
        msg["command"]["default"]["value"]=node_id
        return msg

    def replace_failed_node(self,node_id):
        msg = self.get_message("command","zw_ta.replace_failed_node")
        msg["command"]["default"]["value"]=node_id
        return msg

    def net_ping(self,node_id):
        msg = self.get_message("command","net.ping")
        msg["command"]["default"]["value"][0]=node_id
        return msg


