/**
 * Created with PyCharm.
 * User: alivinco
 * Date: 16/01/15
 * Time: 13:29
 * To change this template use File | Settings | File Templates.
 */

var cy
var current_controller_mode = ""
var countdown_timer_obj = null
function start_clusion_mode(mode,start)
{
    if (mode)current_controller_mode=mode
    else{
        //means inclusion or exclusion stop
        mode = current_controller_mode
    }



    if (mode=="zw_inclusion_mode")
        $("#mode_header").html("Inclusion mode")
    else
        $("#mode_header").html("Exclusion mode")

//    $('#clusion_mode_result').html("Please wait.....")
    if (countdown_timer_obj)clearTimeout(countdown_timer_obj)
    countdown(30)

    if (start==false){
        clearTimeout(countdown_timer_obj)
        $('#clusion_mode_result').html("<h4>Stopped</h4>")
        $('#start_mode_modal').modal('hide')

    }else{
        $('#start_mode_modal').modal('show')
    }


     $.ajax({
      url: "/api/zw_manager",
      method :"POST",
      data: {
        action:mode,
        start:start
      },
      success: function( data ) {
//        console.dir(data)
        console.dir(data)
        clearTimeout(countdown_timer_obj)
        if (data)
        {
            if(current_controller_mode == "zw_inclusion_mode")
            {
                new_dev = data.event.properties.inclusion_report.value.device
                console.log(new_dev.id)
                $('#clusion_mode_result').html("<h4>Device with node id ="+new_dev.id+" was added to the network</h4>")
            }else {
                removed_dev = data.event.default.value
                $('#clusion_mode_result').html("<h4>Device with node id ="+removed_dev+" was removed from the network</h4>")
            }
        }
      }
    });
    //clusion_mode_result

}
function countdown(seconds) {

    if (seconds == 1) {
      $('#clusion_mode_result').html("Controller has timed out");
      return;
    }

    seconds--;
    $('#clusion_mode_result').html(seconds+" seconds left .");
    countdown_timer_obj = setTimeout(countdown, 1000,seconds);
}

function remove_node(node_id)
{
    $('#ping_node_modal').modal('show')
    $('#ping_node_result').html("<h4> Operation in progress , please wait. </h4>")
    $.ajax({
      url: "/api/zw_manager",
      method :"POST",
      data: {action: "remove_failed_node",node_id:node_id},
      success: function( data ) {
         $('#ping_node_result').html("<h4> Command was sent and will be completed in a few seconds. You need to reload page to reflect changes. </h4>")
         setTimeout(function () { $('#ping_node_modal').modal('hide'); }, 5000);
      }
    });
}

function replace_node(node_id)
{
    $('#ping_node_modal').modal('show')
    $('#ping_node_result').html("<h4> Operation in progress , please wait. </h4>")
    $.ajax({
      url: "/api/zw_manager",
      method :"POST",
      data: {action: "replace_failed_node",node_id:node_id},
      success: function( data ) {
         $('#ping_node_result').html("<h4>Now put new device into inclusion mode . </h4>")
         setTimeout(function () { $('#ping_node_modal').modal('hide'); }, 5000);
      }
    });
}

function get_node_info(node_id)
{
    $('#ping_node_modal').modal('show')
    $('#ping_node_result').html("<h4> Operation in progress , please wait. </h4>")
    $.ajax({
      url: "/api/zw_manager",
      method :"POST",
      data: {action: "get_node_info",node_id:node_id},
      success: function( data ) {
            $('#ping_node_result').html("<pre>"+JSON.stringify(data.event.properties.inclusion_report.value,null,2)+"</pre>")
      }
    });
}

function ping_node(node_id)
{
    $('#ping_node_modal').modal('show')
    $('#ping_node_result').html("<h4> Ping in progress , please wait. </h4>")
    $.ajax({
      url: "/api/zw_manager",
      method :"POST",
      data: {action: "ping_node",node_id:node_id},
      success: function( data ) {
            tx_count = data.event.properties.tx_count
            rx_count = data.event.properties.rx_count
            if (tx_count == rx_count) status = "Node is reachable "
            else status = "Node is unreachable "
            $('#ping_node_result').html("<h4>"+status+" (tx:"+tx_count+",rx:"+rx_count+") </h4>")
      }
    });
}

function load_network_graph_data()
{

    $.ajax({
      url: "/api/zw_manager",
      method :"POST",
      data: {
        action: "get_network_graph"
      },
      success: function( data ) {
//        console.dir(data)
        console.dir(data)
        cy.load(data)
      }
    });
}

$(function(){ // on dom ready

$('#network_graph').cytoscape({
  style: cytoscape.stylesheet()
    .selector('node')
      .css({
        'background-color': '#B3767E',
        'width': 'mapData(baz, 0, 7, 7, 40)',
        'height': 'mapData(baz, 0, 7, 7, 40)',
        'content': 'data(id)'
      })
    .selector('edge')
      .css({
        'line-color': '#F2B1BA',
        'target-arrow-color': '#F2B1BA',
        'width': 1,
        'target-arrow-shape': 'triangle',
        'opacity': 0.8,
        'content':'data(weight)',
        'font-size':'6px'
      })
    .selector(':selected')
      .css({
        'background-color': 'black',
        'line-color': 'black',
        'target-arrow-color': 'black',
        'source-arrow-color': 'black',
        'opacity': 1
      })
    .selector('.faded')
      .css({
        'opacity': 0.25,
        'text-opacity': 0
      }),

//  elements: elesJson,

  layout: {
    name: 'cola',
    padding: 30
  },

  ready: function(){
    console.log("ready")
//    load_network_graph_data()

  }
});


cy = $('#network_graph').cytoscape('get');
load_network_graph_data()

//cy.load(elesJson)


}); // on dom ready