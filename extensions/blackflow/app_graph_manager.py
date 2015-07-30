__author__ = 'alivinco'


class AppGraphManager():
    def __init__(self, app_instances):
        self.app_instances = app_instances
        self.max_node_id = 0

    def convert_app_instances_into_graph(self):
        self.nodes = []
        self.edges = []
        # -------PUBLISH-NODES-----------------------------------------------------
        for app_inst in self.app_instances:
            self.nodes.append(app_inst)
            for key, pub_to in app_inst["pub_to"].iteritems():
                # list_of_target_ids = self.__get_target_app_ids_by_pub_topic(pub_to)
                # if len(list_of_target_ids) > 0:
                #     for target_id in list_of_target_ids:
                #         edge = {"from":app_inst["id"],"to":target_id}
                #         if not (edge in self.edges): self.edges.append(edge)
                # else :
                new_id = self.__add_unknown_node(pub_to["topic"])
                edge = {"from": app_inst["id"], "to": new_id}
                if not (edge in self.edges): self.edges.append(edge)

            for key, sub_for in app_inst["sub_for"].iteritems():
                # list_of_target_ids = self.__get_target_app_ids_by_sub_topic(sub_for)
                # if len(list_of_target_ids) > 0:
                #     for target_id in list_of_target_ids:
                #         edge = {"to":app_inst["id"],"from":target_id}
                #         if not (edge in self.edges) : self.edges.append(edge)
                new_id = self.__add_unknown_node(sub_for["topic"])
                edge = {"to": app_inst["id"], "from": new_id}
                if not (edge in self.edges): self.edges.append(edge)

        return {"nodes": self.nodes, "edges": self.edges}

    def __get_next_node_id(self):
        if self.max_node_id == 0:
            for app_inst in self.app_instances:
                if app_inst["id"] > self.max_node_id: self.max_node_id = app_inst["id"]
        self.max_node_id += 1
        return self.max_node_id

    def __add_unknown_node(self, topic, desc=""):
        # check to avoid dublicates
        new_id = self.__get_next_node_id()
        search = filter(lambda node: node["alias"] == topic, self.nodes)
        if len(search) == 0:
            self.nodes.append({"id": new_id, "alias": topic})
        else:
            new_id = search[0]["id"]
        return new_id

    def __get_target_app_ids_by_pub_topic(self, pub_topic):
        result = []
        for app_inst in self.app_instances:
            for key, sub_for in app_inst["sub_for"].iteritems():
                if pub_topic == sub_for:
                    result.append(app_inst["id"])
        return result

    def __get_target_app_ids_by_sub_topic(self, sub_topic):
        result = []
        for app_inst in self.app_instances:
            for key, sub_for in app_inst["pub_to"].iteritems():
                if sub_topic == sub_for:
                    result.append(app_inst["id"])
        return result
