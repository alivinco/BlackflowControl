__author__ = 'alivinco'


import networkx as nx
import matplotlib.pyplot as plt

def test():
    G=nx.Graph()
    G.add_node(1,name="controller 1")
    G.add_node(2,name="repeater 2")
    G.add_node(3,name="node 3")
    G.add_node(4,name="node 4")
    G.add_edge(1,2)
    G.add_edge(1,3)
    G.add_edge(2,4)
    G.add_edge(3,5)
    G.add_edge(2,5)

    shortest_path = nx.shortest_path(G,1,5)

    print shortest_path

    labels = {1:"controller 1",2:"repeater 2",3:"node 3",4:"node 4",5:"node 5"}
    nx.draw_networkx(G,pos=nx.spectral_layout(G),labels = labels,node_color="r")
    nx.draw_networkx(G,pos=nx.spectral_layout(G),labels = labels,node_color="g",nodelist=shortest_path)
    plt.axis('off')
    plt.savefig("path.png")


test()