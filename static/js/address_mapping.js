/**
 * Created with PyCharm.
 * User: aleksandrsl
 * Date: 10.03.14
 * Time: 11:40
 * To change this template use File | Settings | File Templates.
 */

function remove_address(address,msg_class)
{
obj = {"cmd":"remove","address":address,"msg_class":msg_class}
    $.ajax({
      url: "../api/address_manager",
      type: 'POST',
      contentType: 'application/json; charset=utf-8',
      data:  JSON.stringify(obj),
      success: function( data ) {
        location.reload()
      }
    });

}

$(function() {
//    console.log( "ready!" );
   $("#addr_map_table").stupidtable();
});

