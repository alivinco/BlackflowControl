from libs.dmapi.core import Core

__author__ = 'alivinco'

class Binary(Core):
    def factory_reset(self):
        return self.get_message("command","binary.factory_reset")