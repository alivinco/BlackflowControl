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
    }

    $('#start_mode_modal').modal({"show":true})
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


function load_network_graph_data()
{

    $.ajax({
      url: "/api/zw_diagnostics/get_network_graph",
//      data: {
//        zipcode: 97201
//      },
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
        'opacity': 0.8
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