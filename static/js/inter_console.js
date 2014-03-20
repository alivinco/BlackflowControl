/**
 * Created with PyCharm.
 * User: aleksandrsl
 * Date: 27.02.14
 * Time: 15:08
 * To change this template use File | Settings | File Templates.
 */
var wsUri = "http://127.0.0.1:5000/test";
var msg_cache
function start_pooling_cache()
{
    setInterval(load_data,1000);
}


function load_data()
{

    $.ajax({
      url: "../api/get_msg_from_cache/all",
//      data: {
//        zipcode: 97201
//      },
      success: function( data ) {
//        console.dir(data)
        update_elements(data.result)
        msg_cache = data.result
      }
    });
}

function send_command(key,ui_type,value)
{

    if (ui_type=="input_num_field")
    {
        val = parseFloat($("#"+jq_elector(key+"_input")).val())
        console.log(typeof val)
        console.log("var:"+val)

    }else
    {
        val = value
    }

    obj = {"msg_key":key,"user_params":{"value":val}}
    $.ajax({
      url: "../api/send_command",
      type: 'POST',
      contentType: 'application/json; charset=utf-8',
      data:  JSON.stringify(obj),
      success: function( data ) {
        load_data()
      }
    });
}
function jq_elector(str)
{
	return str.replace(/([;&,\.\+\*\~':"\!\^#$%@\[\]\(\)=>\|])/g, '\\$1');
}

function update_elements(msg_cache)
{
    //iterate over all devices
    for(k_item  in msg_cache)
    {
        ui_type = msg_cache[k_item].ui_element
        ui_element_id = k_item
        if(ui_type=="toggle_switch")
        {
            if(msg_cache[k_item].extracted_values.value)
            {
               $("#"+jq_elector(ui_element_id)+"_on").addClass("active")
               $("#"+jq_elector(ui_element_id)+"_off").removeClass("active")
            }else
            {
               $("#"+jq_elector(ui_element_id)+"_on").removeClass("active")
               $("#"+jq_elector(ui_element_id)+"_off").addClass("active")
            }
        }else if(ui_type=="binary_light")
        {
            if(msg_cache[k_item].extracted_values.value)
            {
                $("#"+jq_elector(ui_element_id)).removeClass("alert-danger")
                $("#"+jq_elector(ui_element_id)).addClass("alert-success")
            }
            else
            {
                $("#"+jq_elector(ui_element_id)).removeClass("alert-success")
                $("#"+jq_elector(ui_element_id)).addClass("alert-danger")

            }
        }else if(ui_type=="free_text")
        {

        }else if(ui_type=="sensor_value")
        {
//            console.log("sensor value:"+msg_cache[k_item].extracted_values.value)
            $("#"+jq_elector(ui_element_id)).html("<h3>"+msg_cache[k_item].extracted_values.value+"<small>"+ msg_cache[k_item].extracted_values.unit+"</small></h3>")
//            console.dir($("#"+jq_elector(ui_element_id)))
        }


//        $("#testdiv").html(msg_cache[k_item].ui_element)
    }
}

function open_free_text(key)
{
    $("#free_text_modal").modal('show')
    try{
       if (typeof msg_cache[key].extracted_values.value == "object" )
          out_text = JSON.stringify(msg_cache[key].extracted_values.value)
       else
          out_text = msg_cache[key].extracted_values.value

        $("#free_text_placeholder").html("<pre>"+out_text+"</pre>")
    }catch(err){
       $("#free_text_placeholder").html("<pre>...</pre>")
    }
}

$(function() {
//    console.log( "ready!" );
    load_data()
    start_pooling_cache()
    $("#inter_console_table").stupidtable();
});