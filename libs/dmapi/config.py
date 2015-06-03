from libs.dmapi.core import Core

__author__ = 'alivinco'

class Config(Core):

    def set(self,name,value):
        msg = self.get_message("command","config.set")
        msg["command"]["properties"][name]={"value":value}
        return msg

    def get(self,name):
        msg = self.get_message("command","config.get")
        msg["command"]["default"]["value"]=[name]
        return msg
