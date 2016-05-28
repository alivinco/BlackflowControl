__author__ = 'alivinco'


class AppGraphManager():
    def __init__(self, app_instances, container_id):
        self.app_instances = app_instances
        self.max_node_id = 0
        self.container_id = container_id
        self.nodes = []
        self.edges = []

    def get_id(self,id):
        return "%s_%s"%(self.container_id,id)

    def convert_app_instances_into_graph(self):
        self.nodes = []
        self.edges = []
        # -------PUBLISH-NODES-----------------------------------------------------
        for app_inst in self.app_instances:

            if "schedules" in app_inst :
                app_inst["schedules"] = True if len(app_inst["schedules"]) > 0 else False
                if app_inst["schedules"] :
                    new_id = self.__add_unknown_node("local:time_scheduler")
                    edge = {"to": self.get_id(app_inst["id"]), "from": self.get_id(new_id)}
                    if not (edge in self.edges): self.edges.append(edge)
            app_inst["group"] = self.container_id
            self.nodes.append(app_inst)
            for key, pub_to in app_inst["pub_to"].iteritems():
                new_id = self.__add_unknown_node(pub_to["topic"])
                edge = {"from": self.get_id(app_inst["id"]), "to": self.get_id(new_id)}
                if not (edge in self.edges): self.edges.append(edge)

            for key, sub_for in app_inst["sub_for"].iteritems():
                new_id = self.__add_unknown_node(sub_for["topic"])
                edge = {"to": self.get_id(app_inst["id"]), "from": self.get_id(new_id)}
                if not (edge in self.edges): self.edges.append(edge)

            app_inst["id"] = self.get_id(app_inst["id"])

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
            self.nodes.append({"id": self.get_id(new_id), "alias": topic , "group":self.container_id})
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
