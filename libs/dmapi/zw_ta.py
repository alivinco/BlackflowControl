from libs.dmapi.core import Core

__author__ = 'alivinco'

class ZwTa(Core):
    def get_routing_info(self):
        return self.get_message("command","zw_ta.get_routing_info")

    def get_node_info(self,node_id):
        msg = self.get_message("command","zw_ta.request_inclusion_report")
        msg["command"]["default"]["value"]=node_id
        return msg

    def inclusion_mode(self,start=True,enable_security=True):
        msg = self.get_message("command","zw_ta.inclusion_mode")
        msg["command"]["default"]["value"] = start
        msg["command"]["properties"]["enable_secure_inclusion"] = enable_security
        return msg

    def exclusion_mode(self,start=True):
        msg = self.get_message("command","zw_ta.exclusion_mode")
        msg["command"]["default"]["value"]=start
        return msg

    def learn_mode(self,start=True):
        msg = self.get_message("command","zw_ta.learn_mode")
        msg["command"]["default"]["value"]=start
        return msg

    def controller_shift_mode(self,start=True):
        msg = self.get_message("command","zw_ta.controller_shift_mode")
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

    def neighbor_update(self,node_id):
        msg = self.get_message("command","zw_ta.neighbor_update")
        msg["command"]["default"]["value"][0]=node_id
        return msg

    def hard_reset(self):
        return self.get_message("command","zw_ta.hard_reset")

    def get_controller_full_info(self):
        return self.get_message("command","zw_ta.get_controller_full_info")

    def reset_controller_to_default(self):
        return self.get_message("command","zw_ta.reset_controller_to_default")

    def network_update(self):
        return self.get_message("command","zw_ta.request_network_update_from_suc")

    def get_context(self):
        return self.get_message("command","zw_ta.get_context")


