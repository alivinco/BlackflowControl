from libs.dmapi.core import Core

__author__ = 'alivinco'

class Devicereg(Core):
    def get_device_list(self):
        return self.get_message("command","devicereg.get_device_list")

