from libs.dmapi.core import Core

__author__ = 'alivinco'

class Association(Core):

    def set(self,group,node):
        msg = self.get_message("command","association.set")
        msg["command"]["properties"]["group"]={"value":group}
        msg["command"]["properties"]["devices"]={"value":[node]}
        return msg

    def get(self,group):
        msg = self.get_message("command","association.get")
        msg["command"]["properties"]["group"]={"value":group}
        return msg
