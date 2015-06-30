from libs.dmapi.core import Core

__author__ = 'alivinco'

class Blackflow(Core):
    def context_get(self):
        return self.get_message("command","blackflow.context_get")



