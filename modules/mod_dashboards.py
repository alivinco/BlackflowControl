__author__ = 'alivinco'
import os ,json

class DashboardManager:

    def __init__(self):
        self.app_root_path = os.getcwd()
        self.dash_map_path = os.path.join(self.app_root_path, "configs", "dashboards.json")
        self.load_dashboard_map()

    def load_dashboard_map(self):
        self.dash_map = json.load(file(self.dash_map_path))

    def get_dashboard_map(self,dash_id):
        return self.dash_map

    def get_extended_dashboard_map(self,dash_id,linked_addr_mapping):
        ext_map = []

        for item in linked_addr_mapping:
            if str(item["id"]) in self.dash_map[dash_id]["grid_map"]:
                item["dash_grid_map"] = self.dash_map[dash_id]["grid_map"][str(item["id"])]
                ext_map.append(item)
        return ext_map

    def get_dashboard_grid_size(self,dash_id):
        max_row = 0
        max_col = 0
        for item in self.dash_map[dash_id]["grid_map"].itervalues():
            if max_row < item["row"]:max_row=item["row"]
            if max_col < item["col"]:max_col=item["col"]

        return {"row":max_row,"col":max_col}




if __name__ == "__main__":
    t = DashboardManager()
    from modules.msg_manager import MessageManager
    msg_man = MessageManager()
    # print json.dumps(t.get_dashboard_map(),indent=True)
    linked_map = msg_man.generate_linked_mapping(msg_man.msg_class_mapping, msg_man.address_mapping)
    print json.dumps(t.get_dashboard_grid_size("dash1"),indent=True)

    print json.dumps(t.get_extended_dashboard_map("dash1",linked_map),indent=True)

