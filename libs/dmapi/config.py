from libs.dmapi.core import Core

__author__ = 'alivinco'

class Config(Core):

    def set(self,name,value,size=None):
        msg = self.get_message("command","config.set")
        msg["command"]["properties"] = {}
        if size :
            msg["command"]["properties"][name]={"value":value,"size":size}
        else:
            msg["command"]["properties"][name]={"value":value}
        return msg

    def get(self,name):
        msg = self.get_message("command","config.get")
        msg["command"]["default"]["value"]=[name]
        return msg
