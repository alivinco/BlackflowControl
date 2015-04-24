import json

__author__ = 'alivinco'

class ZwaveTools:
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


if __name__ == "__main__":
    zt = ZwaveTools()
    jobj = json.load(file("tests/poc/network_info.json"))

    print json.dumps(zt.get_network_graph(jobj["event"]["properties"]),indent=True)
