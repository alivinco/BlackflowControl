import json

__author__ = 'alivinco'


class ZwaveTools:
    def __init__(self,msg_man):
        self.msg_man = msg_man

    def get_network_graph(self,nb_table):
        node = {"data":{"id":None}}
        edge = {"data":{"id":None,"weight":0,"source":None,"target":None}}

        nodes = []
        edges = []
        graph = []

        # loop over nodes
        for node , nb_list in nb_table.iteritems():
            nodes.append({"data":{"id":node}})

            # loop over neibhours and generating edges
            for nb_node in nb_list :
                # filtering out back duplicates
                nb_check = filter(lambda nd :(nd["data"]["id"]=="%s_%s"%(nb_node,node)),edges)
                if len(nb_check)==0:
                    edge = {"data":{"id":"%s_%s"%(node,nb_node),"weight":1,"source":node,"target":str(nb_node)}}
                    edges.append(edge)

        graph = {"nodes":nodes,"edges":edges}

        return graph

    def on_message(self, topic, msg_jobj, msg_type, msg_class):

        if topic == "/ta/zw/events":
            # clieanup . Delete device related services after exclusion and all zwave related services after factory reset .
            if msg_jobj["event"]["@type"]=="zw_ta" and msg_jobj["event"]["subtype"]=="exclusion_report":
                self.msg_man.bulk_address_removal("/dev/zw/%s"%msg_jobj["event"]["default"]["value"])
            elif msg_jobj["event"]["@type"]=="binary" and msg_jobj["event"]["subtype"]=="factory_reset":
                self.msg_man.bulk_address_removal("/dev/zw/")

if __name__ == "__main__":
    zt = ZwaveTools()
    jobj = json.load(file("tests/poc/network_info.json"))

    print json.dumps(zt.get_network_graph(jobj["event"]["properties"]),indent=True)
