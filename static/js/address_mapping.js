/**
 * Created with PyCharm.
 * User: aleksandrsl
 * Date: 10.03.14
 * Time: 11:40
 * To change this template use File | Settings | File Templates.
 */

function remove_address(dev_id)
{
obj = {"cmd":"remove","id":dev_id}
    $.ajax({
      url: "../api/address_manager",
      type: 'PUT',
      contentType: 'application/json; charset=utf-8',
      data:  JSON.stringify(obj),
      success: function( data ) {
        location.reload()
      }
    });

}

function open_bulk_address_update()
{
    $("#bulk_address_update_modal").modal('show')
}
function open_bulk_address_delete()
{
    $("#bulk_address_delete_modal").modal('show')
}


$(function() {
//    console.log( "ready!" );
   $("#addr_map_table").stupidtable();
});

