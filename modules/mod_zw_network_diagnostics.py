__author__ = 'alivinco'

# import networkx as nx

class ZwNetworkDiagnostics():

    def get_routing_info(self):
        pass

    def build_graph_from_routing_info(self,routing_info):
        graph=nx.Graph()
        for node_id , neighbors in routing_info["properties"].iteritems():
            for neighbor in neighbors:
                self.graph.add_edge(int(node_id),int(neighbor))
        return graph

    def check_link_between_nodes(self,source_node,target_node):
        pass

    def get_repeaters(self):
        pass

    def get_alarm_devices(self):
        pass

    def run_alarm_device_check(self):
        routing_info = self.get_routing_info()
        graph = self.build_graph_from_routing_info(routing_info)
        list_of_repeaters = self.get_repeaters()
        list_of_alarm_devices = self.get_alarm_devices()

        devices_we_want_to_check = list_of_repeaters+list_of_alarm_devices


