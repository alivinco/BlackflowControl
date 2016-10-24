var instancesGraph;
var instancesGraphData;
function get_node_shape(alias)
{
    if(alias.indexOf("mqtt:") > -1) {
        shape = "box"
        color = "Orange"
    }
    else if(alias.indexOf("local:time_scheduler") > -1){
      shape = "box"
      color = "RosyBrown"
    }
    else if(alias.indexOf("local:") > -1){
      shape = "box"
      color = "Salmon"
    }
    else {
      shape = "ellipse"
      color = "LightGreen" }
    return {"color":color,"shape":shape}
}

function map_role_to_image(role)
{
    var mapping = {
        "lamp":root_uri+"/static/img/icons/illumination.svg",
        "switch":root_uri+"/static/img/icons/power-button.svg",
        "clock":root_uri+"/static/img/icons/clock.svg",
        "temp_sensor":root_uri+"/static/img/icons/thermometer.svg",
        "light_sensor":root_uri+"/static/img/icons/solar-panel.svg",
        "console":root_uri+"/static/img/icons/console.svg",
        "key":root_uri+"/static/img/icons/electronic-key.svg",
        "lock":root_uri+"/static/img/icons/padlock.svg",
        "heating":root_uri+"/static/img/icons/heating.svg",
        "plug":root_uri+"/static/img/icons/plug.svg",
        "motion":root_uri+"/static/img/icons/eye.svg",
        "notification":root_uri+"/static/img/icons/notification.svg",
        "alarm":root_uri+"/static/img/icons/alarm.svg"

    }
    return mapping[role]
}

function transformData(data)
{
    for(i in data.nodes)
    {
        alias = data.nodes[i].alias
        shape = get_node_shape(alias)
        role = data.nodes[i].role
        desc = data.nodes[i].desc
        // app or node
        type = data.nodes[i].type
        var imgUrl = ""
        if (type == "app"){
            data.nodes[i]["label"] = alias +" \n @"+data.nodes[i]["group"]
        }else{
            if (role){
                imgUrl = map_role_to_image(role)
                if (imgUrl != null){
                    data.nodes[i]["label"] = desc
                    data.nodes[i]["image"] = imgUrl
                    shape["shape"] = "image"
                }else {
                    data.nodes[i]["label"] = "r:"+role+" d:"+desc
                }

            }else {
                data.nodes[i]["label"] = alias
            }

        }
        data.nodes[i]["shape"] = shape["shape"]
        data.nodes[i]["color"] = shape["color"]
    }
    for(i in data.edges)
    {
        data.edges[i]["id"] = data.edges[i].from+"_"+data.edges[i].to
        //data.edges[i]["label"] = "1"
    }
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
    return  $.getJSON(root_uri+'/api/app_instances_graph',data, function (data) {
        instancesGraphData = transformData(data)
        instancesGraph.setData(instancesGraphData)
        //console.log(nodeAliasToIdLookup("mqtt:/dev/serial/99/bin_switch/commands"))

    })
}

function loadAnalytics()
{
    data = []
    $.getJSON(root_uri+'/api/analytics',data, function (data) {

        for (i in data)
        {
           from = data[i][0]
           from_id = nodeAliasToIdLookup(from)
           to_id = nodeAliasToIdLookup(data[i][1])
           if (from_id && to_id) {
               count_v = data[i][2]
               id = from_id + "_" + to_id
               instancesGraphData.edges.update({"id": id, "label": count_v})
           }
        }

    })
}

function startPoolingAnalytics()
{
    loadAnalytics()
    setInterval(loadAnalytics,10000);
}


function repositionaNodes()
{
    instancesGraphData.nodes.forEach(function(node) {
        npos = localStorage.getItem("npos_" + node.id)
        if (npos) {
            npos = JSON.parse(npos)
            instancesGraphData.nodes.update(npos)
        }
    })
}

function updateNodePosition(nodeId,xPos,yPos){
    console.log(nodeId)
    if (nodeId){
        upd = {id:nodeId,x:xPos,y:yPos,fixed:true}
        instancesGraphData.nodes.update(upd)
        localStorage.setItem("npos_"+nodeId,JSON.stringify(upd))
    }
}

function initGraph() {

    // create a network
    var container = document.getElementById('app_instances_graph_div');
    // provide the data in the vis format
    var data = {};
    var options = { edges:{arrows: 'to',smooth:false},
                   layout:{hierarchical: {
                          enabled:false,
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
    // initialize your network!
    instancesGraph = new vis.Network(container, data, options);
    instancesGraph.on("dragEnd",function(obj){
        //console.dir(obj)
        nodeId = obj.nodes[0]
        updateNodePosition(nodeId,obj.pointer.canvas.x,obj.pointer.canvas.y)
        console.dir(instancesGraphData.nodes)
    })
    instancesGraph.on("dragStart",function(obj){
        //console.dir(obj)
        nodeId = obj.nodes[0]
        if (nodeId) {
            instancesGraphData.nodes.update({id: nodeId, fixed: false})
        }
    })
    instancesGraph.on("doubleClick",function(obj){
        console.dir(obj)
        nodeId = obj.nodes[0]

        if (nodeId) {
            node = instancesGraphData.nodes.get(nodeId)
            if (node.type == "app"){
                console.dir(node)
                selectedInstanceId = node.id
                selectedAppFullName = node.app_full_name
                selectedContainer = node.group
                $("#mod_inst_name").html(node.alias)
                $("#mod_app_full_name").html(node.app_full_name)
                $("#mod_comments").html(node.comments)
                $("#mod_container").html(node.group)
                $("#appInfoModal").modal({show:true})
            }else if (node.type == "node"){
                $("#mod_node_msg_type").html(node.msg_type)
                $("#mod_node_topic_addr").html(node.alias)
                $("#mod_node_role").html(node.role)
                $("#mod_node_description").html(node.description)
                $("#mod_node_container").html(node.group)
                $("#nodeInfoModal").modal({show:true})
            }

        }
    })
}
function openInstanceConfig()
{
  idSplit = selectedInstanceId.split("_")
  //window.location = root_uri+"/ui/app_instance_config?id="+idSplit[1]+"&app_name="+selectedAppFullName+"&container_id="+selectedContainer
  window.open(root_uri+"/ui/app_instance_config?id="+idSplit[1]+"&app_name="+selectedAppFullName+"&container_id="+selectedContainer)
}
function openAppConfig()
{
  //window.location = root_uri+"/ui/app_editor?app_name="+selectedAppFullName+"&container_id="+selectedContainer
  window.open(root_uri+"/ui/app_editor?app_name="+selectedAppFullName+"&container_id="+selectedContainer)
}

 $(function(){

    initGraph()
    loadGraph().done(function(data){
        repositionaNodes()
        startPoolingAnalytics()
    })
    //document.getElementById('draw').onclick = set_dates()
})
