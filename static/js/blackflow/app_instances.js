var instancesGraph;

function get_node_shape(alias)
{
    if(alias.indexOf("mqtt:") > -1)
      shape = "box"
    else if(alias.indexOf("local:") > -1)
      shape = "box"
    else
      shape = "circle"
    return shape
}

function transformData(data)
{
    for(i in data.nodes)
    {
        alias = data.nodes[i].alias
        data.nodes[i]["label"] = alias

        data.nodes[i]["shape"] = get_node_shape(alias)

    }
    //for(i in data.edges)
    //{
    //    data.edges[i]["arrows"] = "to"
    //}
    console.dir(data)
    result = {
        edges : new vis.DataSet(data.edges),
        nodes : new vis.DataSet(data.nodes)
    }
    return result
}

function loadGraph()
{
    data = []
    $.getJSON('/api/blackflow/app_instances_graph',data, function (data) {
        data = transformData(data)
        instancesGraph.setData(data)
    })
}

function initGraph() {

    // create a network
    var container = document.getElementById('app_instances_graph_div');
    // provide the data in the vis format
    var data = {};
    var options = {edges:{arrows: 'to'},
                   layout:{hierarchical: {
                          enabled:true,
                          levelSeparation: 250,
                          direction: 'LR',   // UD, DU, LR, RL
                          sortMethod: 'hubsize' // hubsize, directed
                        }},
                    "physics": {
                            "maxVelocity": 26,
                            "solver": "repulsion",
                            "timestep": 0.48
                          }
    };
    //var options = {
    //            layout: {
    //                hierarchical: {
    //                    direction: directionInput
    //                }
    //            }
    //        };
    // initialize your network!
    instancesGraph = new vis.Network(container, data, options);
}
 $(function(){

    initGraph()
    loadGraph()
    //document.getElementById('draw').onclick = set_dates()
})
