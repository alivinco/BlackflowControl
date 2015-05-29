/**
 * Created with PyCharm.
 * User: aleksandrsl
 * Date: 27.02.14
 * Time: 15:08
 * To change this template use File | Settings | File Templates.
 */
var msg_cache

function start_pooling_cache()
{
    setInterval(load_data,1000);
}


function load_data()
{

    $.ajax({
      url: "/api/get_msg_from_cache/all",
//      data: {
//        zipcode: 97201
//      },
      success: function( data ) {
//        console.dir(data)
        msg_cache = data.result
        if (mode=="normal") update_elements(data.result)

      }
    });
}

function send_command(key,ui_type,value)
{
    obj = null
    if (ui_type=="input_num_field")
    {
        val = parseFloat($("#"+jq_elector(key+"_input")).val())
//        console.log(typeof val)
//        console.log("var:"+val)

    }else if (ui_type=="input_text_field")
    {
        val = $("#"+jq_elector(key+"_input")).val()
    }

    else if (ui_type=="msg_class_ui")
    {
       div_el = $("#"+jq_elector(key))
       user_params = {}
       div_el.find('input,select').each(function(index){
//           console.log($(this)[0].value)
           input_id = $(this)[0].id
           input_value = $(this)[0].value
           user_params[input_id]=input_value
       })

       obj = {"msg_key":key,"user_params":user_params,"mode":mode}
//       console.dir(obj)
    } else
    {
        val = value
//        console.log(value)
    }

    if(!obj) obj = {"msg_key":key,"user_params":{"value":val},"mode":mode}
    $.ajax({
      url: "/api/send_command",
      type: 'POST',
      contentType: 'application/json; charset=utf-8',
      data:  JSON.stringify(obj),
      success: function( data ) {

       if (mode=="normal") load_data()
      }
    });
}
function jq_elector(str)
{
	return str.replace(/([;&,\.\+\*\~':"\!\^#$%@\[\]\(\)=>\|])/g, '\\$1');
}
function format_datetime(ts)
{
    return ts.getUTCFullYear()+"-"+(ts.getUTCMonth()+1)+"-"+ts.getUTCDate()+" "+ts.getUTCHours()+":"+ts.getUTCMinutes()+":"+ts.getUTCSeconds()
}
function update_elements(msg_cache)
{
    //iterate over all devices
    for(k_item  in msg_cache)
    {
        ui_type = msg_cache[k_item].ui_element
        ui_element_id = k_item
//        check_for_inclusion(k_item,msg_cache[k_item])
        // update timestamp
        ts = new Date(msg_cache[k_item].timestamp_iso)
        $("#"+jq_elector(k_item)+"_msg_time").html(format_datetime(ts))

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
var last_inclusion_timestamp = ""

function check_for_inclusion(key,item)
{


    if(item.raw_msg.event)
        if(item.raw_msg.event.type == "inclusion" && item.timestamp_iso != last_inclusion_timestamp )
        {

           if (last_inclusion_timestamp!="")
           {
            last_inclusion_timestamp = item.timestamp_iso
            open_free_text(key)
           }else
           {
            last_inclusion_timestamp = item.timestamp_iso
              // open_free_text(key)
           }
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
       console.dir(err)
       $("#free_text_placeholder").html("<pre>...</pre>")
    }
}

function initi_slider()
{
    if ($("input[ui_ext_type='slider']").length>0)
    {
    $("input[ui_ext_type='slider']").slider({min:0,max:100,tooltip: 'always'});
    $("input[ui_ext_type='slider']").on('slideStop', function(slideEvt) {
	    id = slideEvt.target.id.replace("_input","")
        console.dir(slideEvt)
        value = slideEvt.value
        console.log(value)
        send_command(id,'slider',value); return false
    });
    }
}

function update_dropdown_input(dd_id,value)
{
    $("#"+jq_elector(dd_id)).val(value)
}

