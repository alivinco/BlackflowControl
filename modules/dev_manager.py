__author__ = 'alivinco'
import os ,json

class DeviceManager:

    def __init__(self,msg_manager):
        self.app_root_path = os.getcwd()
        self.device_templates_path = os.path.join(self.app_root_path, "configs", "device_templates.json")
        self.devices_path = os.path.join(self.app_root_path, "configs", "devices.json")
        self.device_templates = json.load(file(self.device_templates_path))
        self.devices = self.load_devices()
        self.msg_manager = msg_manager

    def load_devices(self):
        devices = json.load(file(self.devices_path))
        # iterating over devices and extending the structure with template definition .
        for item in devices:
            d  = filter(lambda dev: (item["dev_id"] == dev["id"] ),self.device_templates)
            if len(d)>0:
               item["device"] = d[0]

        return devices

    def get_devices(self):
        return self.devices

    def add_device(self,template_id):
        pass


if __name__ == "__main__":
    t = DeviceManager()
    print json.dumps(t.get_devices(),indent=True)
