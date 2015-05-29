from libs.dmapi.core import Core

__author__ = 'alivinco'

class Devicereg(Core):
    def get_device_list(self):
        return self.get_message("command","devicereg.get_device_list")

    def get_device_by_id(self,device_id):
        msg = self.get_message("command","devicereg.get_device_list")
        msg["command"]["properties"]["search"]={"Id":device_id}
        return msg

    def update(self,search_map,update_map):

        """
         Fields in search and update maps should correspond to fields in data model
        :param search_map: for instance {"Id":1}
        :param update_map: for instance {"Alias":"Demo"}
        """
        msg = self.get_message("command","devicereg.update")
        msg["command"]["properties"]["search"] = search_map
        msg["command"]["properties"]["update"] = update_map
        return msg

    def delete(self,devicereg_id):
        msg = self.get_message("command","devicereg.delete")
        msg["command"]["default"]["value"]=devicereg_id
        return msg

    def get_version(self):
        return self.get_message("command","devicereg.version")
