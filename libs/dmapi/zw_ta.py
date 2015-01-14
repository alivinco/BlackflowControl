from libs.dmapi.core import Core

__author__ = 'alivinco'

class ZwTa(Core):
    def get_routing_info(self):
        return self.get_message("command","zw_ta.get_routing_info")

