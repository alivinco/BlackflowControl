__author__ = 'alivinco'
import os ,json
import logging



class DashboardManager:

    def __init__(self):
        self.app_root_path = os.getcwd()
        self.dash_map_path = os.path.join(self.app_root_path, "configs", "dashboards.json")
        self.load_dashboard_map()
        self.log = logging.getLogger("bf_web")

    def load_dashboard_map(self):
        self.dash_map = json.load(file(self.dash_map_path))

    def get_dashboard_map(self,dash_id=None):
        if dash_id:
            return self.dash_map[dash_id]
        else :
            return self.dash_map

    def get_extended_dashboard_map(self,dash_id,linked_addr_mapping):
        ext_map = []

        for item in linked_addr_mapping:
            if str(item["id"]) in self.dash_map[dash_id]["grid_map"]:
                item["dash_grid_map"] = self.dash_map[dash_id]["grid_map"][str(item["id"])]
                ext_map.append(item)
        return ext_map

    def get_dashboard_grid_size(self,dash_id,group=0):
        max_y = 0
        max_x = 0
        for item in self.dash_map[dash_id]["grid_map"].itervalues():
            if item["group"]==group:
                if max_y < item["y"]:max_y=item["y"]
                if max_x < item["x"]:max_x=item["x"]

        return {"y":max_y,"x":max_x}

    def serialize_dashboard(self):
        self.log.info("Serializing dashboard to file " + self.dash_map_path)
        f = open(self.dash_map_path, "w")
        f.write(json.dumps(self.dash_map, indent=True))
        f.close()

    def update_service(self,dash_id,service_id,service_name):
        """
        Method updates service parameters within dashboard .
        :param dash_id:
        :param service_id: service_id from address_mapping
        :param service_name: service human readable name
        """
        service = self.dash_map[dash_id]["grid_map"][service_id]
        service["service_name"] = service_name
        self.serialize_dashboard()

    def update_group(self,dash_id,group_id,x_size=None,y_size=None,name=None):
        if group_id == -1 :
            new_id = 1
            new_group = {"y_size": y_size,
                         "x_size": x_size,
                         "description": name,
                         "name": name,
                         "id": new_id
                        }
            self.dash_map[dash_id]["groups"].append(new_group)
        else :
            # update
            group = filter(lambda gr : (gr.id==group_id),self.dash_map[dash_id]["groups"])[0]
            if x_size: group.x_size = x_size
            if y_size: group.y_size = y_size
            if name :group.name = name
        self.serialize_dashboard()


    def delete_service_from_dashboard(self, dash_id, service_id):
        """
        The method removes a service from a dashboard.
        :param dash_id:
        :param group:
        :param service_id:
        """
        del self.dash_map[dash_id]["grid_map"][service_id]
        self.log.info("Service with id = "+str(service_id)+" was deleted from dashboard "+dash_id)
        self.serialize_dashboard()

    def change_service_position(self, dash_id, movable_service_id, drop_service_id, start_x_position, start_y_position, dest_x_position,
                     dest_y_position, start_group_id, dest_group_id):
        """
        The method moves one service from position A to position B , if position is already occupied by another service ,
        then the service goes to position A
        :param dash_id: Dashboard ID
        :param movable_service_id: Id of a service which is picked up by user and dragged to new position . Service A
        :param drop_service_id: Id of service B
        :param start_x_pos:
        :param start_y_pos:
        :param dest_x_position:
        :param dest_y_position:
        :param old_group_id:
        :param new_group_id:
        """
        movable_service = self.dash_map[dash_id]["grid_map"][movable_service_id]
        #let's change movable service coordinates to new ones
        movable_service["x"] = dest_x_position
        movable_service["y"] = dest_y_position
        movable_service["group"] = dest_group_id

        if drop_service_id:
            drop_service = self.dash_map[dash_id]["grid_map"][drop_service_id]
            drop_service["x"] = start_x_position
            drop_service["y"] = start_y_position
            drop_service["group"] = start_group_id
        self.serialize_dashboard()


    def add_service_to_dashboard(self,dash_id,group_id,addr_id,x_pos="auto",y_pos="auto",service_name="",layout_type="grid"):
        """
        The method adds a service (sensor value , button , binary representation) to the dashboard .
        :param dash_id: Dashboard Id
        :param group_id: Groups id , groups is a way for grouping services within a dashboards
        :param addr_id: service address id , it comes from address_mapping.json
        :param x_pos: panel x position, in grid it is a xumn
        :param y_pos: panel y position, in grid it is a y
        :param layout_type: layout type , so far "grid" is the only supported layout
        """
        grid_size = self.get_dashboard_grid_size(dash_id,group_id)
        x_size = grid_size["x"]
        y_size = grid_size["y"]

        group = filter(lambda gr : gr["id"]==group_id,self.dash_map[dash_id]["groups"])[0]
        # print self.dash_map[dash_id]["grid_map"][0]["y"]
        if x_pos == "auto" or y_pos=="auto":
            # let's check if last xumn of last y is not empty
            last_y = filter(lambda item :(item["y"]==grid_size["y"] and item["x"]==grid_size["x"]),self.dash_map[dash_id]["grid_map"].values())
            if len(last_y):
                # last y is busy , let's add new service to first xumn of next y
                y_pos = y_size+1
                x_pos = 1
                if y_pos > group["y_size"]:group["y_size"] = y_pos
            else:
                y_pos = y_size
                x_pos = x_size
        else :
            x_pos = int(x_pos)
            y_pos = int(y_pos)



        position = {"y":y_pos,"x":x_pos,"group":group_id,"service_name":service_name}
        self.log.info("Adding new service to dashboard . Service address = "+str(addr_id)+" position = "+str(position))
        self.dash_map[dash_id]["grid_map"][addr_id]= position
        self.serialize_dashboard()


if __name__ == "__main__":
    t = DashboardManager()
    from modules.msg_manager import MessageManager
    msg_man = MessageManager()
    # print json.dumps(t.get_dashboard_map(),indent=True)
    linked_map = msg_man.generate_linked_mapping(msg_man.msg_class_mapping, msg_man.address_mapping)
    print json.dumps(t.get_dashboard_grid_size("dash1"),indent=True)

    print json.dumps(t.get_extended_dashboard_map("dash1",linked_map),indent=True)
    t.add_service_to_dash("dash1","default","122")

