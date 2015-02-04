from libs.dmapi.core import Core

__author__ = 'alivinco'

class ZwTa(Core):
    def get_routing_info(self):
        return self.get_message("command","zw_ta.get_routing_info")

    def inclusion_mode(self,start=True):
        msg = self.get_message("command","zw_ta.inclusion_mode")
        msg["command"]["default"]["value"]=start
        return msg

    def exclusion_mode(self,start=True):
        msg = self.get_message("command","zw_ta.exclusion_mode")
        msg["command"]["default"]["value"]=start
        return msg

