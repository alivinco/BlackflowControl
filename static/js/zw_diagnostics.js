/**
 * Created with PyCharm.
 * User: alivinco
 * Date: 16/01/15
 * Time: 13:29
 * To change this template use File | Settings | File Templates.
 */

var cy

function start_clusion_mode(mode,start)
{
    $('#clusion_mode_result').html("Please wait.....")
    $('#start_mode_modal').modal({"show":true})
     $.ajax({
      url: "/api/zw_manager",
      method :"POST",
      data: {
        action:"zw_inclusion_mode",
        start:start
      },
      success: function( data ) {
//        console.dir(data)
        console.dir(data)
        console.log(data.event.properties.inclusion_report.value.device.id)
        $('#clusion_mode_result').html("<h4>Added new device with Node id ="+data.event.properties.inclusion_report.value.device.id+"</h4>")
      }
    });
    //clusion_mode_result


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