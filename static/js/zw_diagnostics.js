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
var operation_start_time = 0

function get_server_info()
{
    return $.ajax({
      url: root_uri+"/api/get_server_info",
      method :"GET",
      error:function(err)
      {
          alert("Error while getting server info.")
      }
    });

}

function start_clusion_mode(mode,start,enable_security)
{
    enable_security = typeof enable_security !== 'undefined' ? enable_security : true;

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
    countdown(60)

    if (start==false){
        clearTimeout(countdown_timer_obj)
        clearInterval(history_timer)
        $('#clusion_mode_result').html("<h4>Stopped</h4>")
        $('#start_mode_modal').modal('hide')

    }else{
         $('#clusion_mode_result').html("")
        $('#start_mode_modal').modal('show')
    }
    get_server_info().then(function(data){

        console.dir(data)
        operation_start_time = data.time_milis

        if (start) {
           history_timer = pull_history_from_server(true)

        }

         $.ajax({
          url: root_uri+"/api/zw_manager",
          method :"POST",
          data: {
            action:mode,
            start:start,
            enable_security:enable_security
          },
          success: function( data ) {
            console.dir(data)
            clearTimeout(countdown_timer_obj)
            clearInterval(history_timer)
            pull_history_from_server(false)
            if (data)
            {
                if (data.event)
                    if(current_controller_mode == "zw_inclusion_mode")
                    {
                        new_dev = data.event.properties.inclusion_report.value
                        $('#clusion_mode_result').html("<p><h4>Device with node id ="+new_dev.device.id+" was added to the network</h4></p>")
                        $('#clusion_mode_status').html("<p>Report is complete = "+data.event.properties.is_complete+". Critical errors = "+data.event.properties.critical_errors+" </p>")
                    }else {
                        removed_dev = data.event.default.value
                        $('#clusion_mode_result').html("<p><h4>Device with node id ="+removed_dev+" was removed from the network</h4></p>")
                    }
            }
          }
        });
    })
    //clusion_mode_result

}
// stop_message_resolver should be a function which should return true if the message final message .
// function returns promise . Invoker can use progress(data) function or/and done(data) to receive events
// topic returns response whenever topic and msg_type match the values in message
// the function itself will run until stop_msg_resolver returns true or timesout
var global_pool_request_xhr = null
function pool_messages_from_server(topic,msg_type,stop_msg_resolver,timeout)
{

       var def = $.Deferred();
       var isTimeout = false
       if(msg_type) cor_type = "MSG_TYPE"
       else cor_type = "NO_COR_ID"

       function do_request() {
           var prom = $.ajax({
               url: root_uri+"/api/wait_for_msg",
               method: "GET",
               data: {topic: topic, correlation_type: cor_type, msg_type: msg_type, timeout: 35},
           });
           global_pool_request_xhr = prom
           prom.done(function (data) {
               //console.dir(data)
               global_pool_request_xhr = null
               def.notify(data)
               if (data)
                   if (stop_msg_resolver(data))
                          def.resolve(data)
               else if(isTimeout)
                  def.reject()
               else
                 do_request()

           })
       }
       if (global_pool_request_xhr) {
           global_pool_request_xhr.abort()
           global_pool_request_xhr = null
       }
       do_request()
       if (timeout) setTimeout(function(){isTimeout=true},timeout)
       return def.promise()
}
// log output mutex , to prevent several callbacks to write to the same log output.
function pull_history_from_server(auto_pool)
{

       var def = $.Deferred();
       var isTimeout = false
       var startTime = Math.floor(operation_start_time / 1000)

       function do_request() {
           stopTime = Math.floor(Date.now() / 1000)+5000
           var prom = $.ajax({
               url: root_uri+"/api/get_msg_history",
               method: "GET",
               data: {start: startTime},
           });
           global_pool_request_xhr = prom
           prom.done(function (data) {
               if (data.length>0)  {
                   $('#clusion_log').html("")
                   $.each(data, function (index, value) {
                         event = JSON.parse(value.msg).event
                         if (event.subtype!="inclusion_report") {
                             if (event.subtype=="status_code") {
                                 $('#clusion_log').append("<p><h5>" + index + ". ERROR: " + event.properties.error + "</h5></p>")
                             }else{
                                 $('#clusion_log').append("<p><h5>" + index + ". " + event.default.value + "</h5></p>")
                             }
                         }
                   })
               }

           })
       }
       time = null
       if (auto_pool)
           {timer = setInterval(do_request,1000)}
       else
           {do_request()}

       return timer
}

function test_pool()
{
    prom = pool_messages_from_server("/ta/zw/events","net.ping_report",function(){return true},60000)
    prom.progress(function(data){
        console.log("Ping response")
        console.dir(data)
    })
    prom.done(function(data){console.log("Done!!")})
}

function countdown(seconds) {

    if (seconds == 1) {
      $('#countdown_id').html("Controller has timed out");
      return;
    }

    seconds--;
    $('#countdown_id').html(seconds+" seconds left .");
    countdown_timer_obj = setTimeout(countdown, 1000,seconds);
}

function remove_node(node_id)
{
    $('#ping_node_modal').modal('show')
    $('#ping_node_result').html("<h4> Operation in progress , please wait. </h4>")
    $.ajax({
      url: root_uri+"/api/zw_manager",
      method :"POST",
      data: {action: "remove_failed_node",node_id:node_id},
      success: function( data ) {
         //$('#ping_node_result').html("<h4> Command was sent and will be completed in a few seconds. You need to reload page to reflect changes. </h4>")
        prom = pool_messages_from_server("/ta/zw/events", "zw_ta.remove_failed_node_report", function (data) {
             default_value = data.event.default.value
             if (default_value=="ZW_FAILED_NODE_NOT_REMOVED"|| default_value=="FAILED_NODE_NOT_FOUND")
                return true
             else return false
        }, 30000)
        prom.progress(function (data) {
            if (data) $('#ping_node_result').html("<h4>Node remove status : " + data.event.default.value + "</h4>")
        })
        prom.done(function (data) {
            if (data) $('#ping_node_result').html("<h4>Node removed with status : " + data.event.default.value + "</h4>")
        })
        setTimeout(function () { $('#ping_node_modal').modal('hide'); }, 30000);
      }
    });
}

function replace_node(node_id)
{
    $('#ping_node_modal').modal('show')
    $('#ping_node_result').html("<h4> Operation in progress , please wait. </h4>")
    $.ajax({
      url: root_uri+"/api/zw_manager",
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
      url: root_uri+"/api/zw_manager",
      method :"POST",
      data: {action: "get_node_info",node_id:node_id},
      success: function( data ) {
          html_r = "<pre>"+JSON.stringify(data.event.properties.inclusion_report.value,null,2)+"</pre>"
          $('#ping_node_result').html(html_r+"<p>Report is complet = "+data.event.properties.is_complete+" , Critical errors = "+data.event.properties.critical_errors+" </p>")
      }
    });
}

function nb_update(node_id)
{
    $('#ping_node_modal').modal('show')
    $('#ping_node_result').html("<h4> Neighbour redisovery is in progress , please wait. </h4>")
     //status = data.event.default.value
            //$('#ping_node_result').html("<h4> Operation completed with status "+status+"</h4>")
    prom = pool_messages_from_server("/ta/zw/events", "zw_ta.neighbor_update_report", function (data) {
             default_value = data.event.default.value
             if (default_value=="REQUEST_NEIGHBOR_UPDATE_DONE"||default_value=="REQUEST_NEIGHBOR_UPDATE_FAILED")
                return true
             else return false
        }, 60000)
    prom.progress(function (data) {
            if (data) $('#ping_node_result').html("<h4>Operation status has changed to : " + data.event.default.value + "</h4>")
        })
    prom.done(function (data) {
            if (data) $('#ping_node_result').html("<h4>Neighbour redisovery completed with status : " + data.event.default.value + "</h4>")
        })

    $.ajax({
      url: root_uri+"/api/zw_manager",
      method :"POST",
      data: {action: "neighbor_update",node_id:node_id},
      success: function( data ) {

        setTimeout(function () { $('#ping_node_modal').modal('hide'); }, 60000);
      }
    });
}

function learn_mode(start)
{
  if (start) {
        $('#learn_mode_result').html("<h4>Operation is in progress.</h4>")
        $('#learn_mode_modal').modal('show')
    }else {
      $('#learn_mode_modal').modal('hide')
  }
  $.ajax({
      url: root_uri+"/api/zw_manager",
      method :"POST",
      data: {action: "learn_mode",start:start},
      success: function( data ) {
        $('#learn_mode_result').html("<h4>Learn mode has finished with status : "+data.event.default.value+"</h4>")
      }
    });
}

function controller_shift(start)
{

    if (start) {
        $('#cshift_result').html("<h4>Operation is in progress.</h4>")
        $('#start_cshift_modal').modal('show')
    }else {
        $('#start_cshift_modal').modal('hide')
    }

    prom = pool_messages_from_server("/ta/zw/events", "zw_ta.inclusion_stage", function (data) {
             default_value = data.event.default.value
             if (default_value=="ADD_NODE_STATUS_DONE"||default_value=="ADD_NODE_STATUS_FAILED")
                return true
             else return false
        }, 60000)
    prom.progress(function (data) {
            if (data) $('#cshift_result').html("<h4>Operation changed status to : " + data.event.default.value + "</h4>")
        })
    prom.done(function (data) {
            if (data) $('#cshift_result').html("<h4>Controller shift completed with status : " + data.event.default.value + "</h4>")
        })

    $.ajax({
      url: root_uri+"/api/zw_manager",
      method :"POST",
      data: {action: "controller_shift_mode",start:start},
      success: function( data ) {
        setTimeout(function () { $('#cshift_result').modal('hide'); }, 60000);
      }
    });
}

function ping_node(node_id)
{
    $('#ping_node_modal').modal('show')
    $('#ping_node_result').html("<h4> Ping in progress , please wait. </h4>")
    $.ajax({
      url: root_uri+"/api/zw_manager",
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

function hard_reset()
{
    $('#ping_node_modal').modal('show')
    $('#ping_node_result').html("<h4> Reseting zwave module </h4>")
    $.ajax({
      url: root_uri+"/api/zw_manager",
      method :"POST",
      data: {action: "hard_reset"},
      success: function( data ) {
            $('#ping_node_result').html("<h4>Zwave module reset completed with status = "+data.event.default.value+" </h4>")
      }
    });
}

function get_controller_full_info()
{
    $('#ping_node_modal').modal('show')
    $('#ping_node_result').html("<h4> Requesting information from zwave module.</h4>")
    $.ajax({
      url: root_uri+"/api/zw_manager",
      method :"POST",
      data: {action: "get_controller_full_info"},
      success: function( data ) {
            $('#ping_node_result').html("<pre>"+JSON.stringify(data.event.properties,null,2)+"</pre>")
      }
    });
}

function network_update()
{
    $('#ping_node_modal').modal('show')
    $('#ping_node_result').html("<h4> Requesting network update from SUC.</h4>")
    $.ajax({
      url: root_uri+"/api/zw_manager",
      method :"POST",
      data: {action: "network_update"},
      success: function( data ) {
            $('#ping_node_result').html("<h4> Network update completed with status = "+data.event.default.value+" </h4>")
      }
    });
}

function reset_controller_to_default()
{
    $('#ping_node_modal').modal('show')
    $('#ping_node_result').html("<h4> Reseting controller to default .</h4>")
    $.ajax({
      url: root_uri+"/api/zw_manager",
      method :"POST",
      data: {action: "reset_controller_to_default"},
      success: function( data ) {
            $('#ping_node_result').html("<h4>Reset completed with status = "+data.event.properties.status+" </h4>")
      }
    });
}

function load_network_graph_data()
{

    $.ajax({
      url: root_uri+"/api/zw_manager",
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