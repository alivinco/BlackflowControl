/**
 * Created with PyCharm.
 * User: alivinco
 * Date: 04/02/15
 * Time: 10:57
 * To change this template use File | Settings | File Templates.
 */


function open_update_dr_field_modal(device_id,field_name,value)
{

    $("#field_name_label").html(field_name)
    $("#field_name").val(field_name)
    $("#device_id").val(device_id)
    $("#field_value").val(value)

    $("#dr_field_update_modal").modal('show')
}



function execute_devreg_cmd(cmd,device_id,redirect)
{
    $.ajax({
      url: root_uri+"/api/dr_browser",
      method :"POST",
      data: {action: cmd,device_id:device_id},
      success: function( data ) {
            if (redirect)
                location.href = redirect
            else
                location.reload();
      },
      error:function(xhr,textStatus,error)
      {
          alert(error)
      }

    });
}
