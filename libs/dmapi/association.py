from libs.dmapi.core import Core

__author__ = 'alivinco'


class Association(Core):

    def set(self,group,node,endpoint=None):
        if endpoint:
            msg = self.get_message("command","association.endpoint_set")
            msg["command"]["properties"]["group"] = group
            msg["command"]["properties"]["devices"] = [{"device": node, "endpoint": endpoint}]
        else:
            msg = self.get_message("command","association.set")
            msg["command"]["properties"]["group"] = {"value": int(group)}
            msg["command"]["properties"]["devices"] = {"value": [int(node)]}
        return msg

    def get(self,group):
        msg = self.get_message("command","association.get")
        msg["command"]["properties"]["group"]={"value":int(group)}
        return msg