var instancesGraph;
var instancesGraphData;
function get_node_shape(alias)
{
    if(alias.indexOf("mqtt:") > -1) {
        shape = "box"
        color = "Orange"
    }
    else if(alias.indexOf("local:") > -1){
      shape = "box"
      color = "Salmon"
    }
    else {
      shape = "circle"
      color = "LightGreen" }
    return {"color":color,"shape":shape}
}

function transformData(data)
{
    for(i in data.nodes)
    {
        alias = data.nodes[i].alias
        data.nodes[i]["label"] = alias
        shape = get_node_shape(alias)
        data.nodes[i]["shape"] = shape["shape"]
        data.nodes[i]["color"] = shape["color"]

    }
    for(i in data.edges)
    {
        data.edges[i]["id"] = data.edges[i].from+"_"+data.edges[i].to
        //data.edges[i]["label"] = "1"
    }
    console.dir(data)
    result = {
        edges : new vis.DataSet(data.edges),
        nodes : new vis.DataSet(data.nodes)
    }
    return result
}

function updateAllEdgesWhichStartsFrom(nodeId,label)
{
    //for i in instancesGraphData.edges.ge
}

function nodeAliasToIdLookup(alias)
{
    var node = instancesGraphData.nodes.get({filter: function (item) {
                                                return (item.alias == alias);
                                              } });
    if (node.length > 0)
        return node[0].id
    else return null
}

function showAnalytics(data)
{

}

function loadGraph()
{
    data = []
    return  $.getJSON('/api/blackflow/app_instances_graph',data, function (data) {
        instancesGraphData = transformData(data)
        instancesGraph.setData(instancesGraphData)
        //console.log(nodeAliasToIdLookup("mqtt:/dev/serial/99/bin_switch/commands"))

    })
}

function loadAnalytics()
{
    data = []
    $.getJSON('/api/blackflow/analytics',data, function (data) {

        for (i in data.link_counters)
        {
           from = data.link_counters[i][0]
           from_id = nodeAliasToIdLookup(from)
           to_id = nodeAliasToIdLookup(data.link_counters[i][1])
           if (from_id && to_id) {
               count_v = data.link_counters[i][2]
               id = from_id + "_" + to_id
               instancesGraphData.edges.update({"id": id, "label": count_v})
           }
        }

    })
}

function startPoolingAnalytics()
{
    loadAnalytics()
    setInterval(loadAnalytics,2000);
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
    loadGraph().done(function(data){
        startPoolingAnalytics()
    })
    //document.getElementById('draw').onclick = set_dates()
})
