/**
 * Created with PyCharm.
 * User: alivinco
 * Date: 11/03/14
 * Time: 13:18
 * To change this template use File | Settings | File Templates.
 */

function approve_msg_class(address,msg_class,is_approved)
{
   // add class to address msg_class mapping if that was approved otherwise move to block list
   obj = {"address":address,"msg_class":msg_class,"is_approved":is_approved}
   $.ajax({
      url: root_uri+"/api/approve_msg_class",
      type: 'POST',
      contentType: 'application/json; charset=utf-8',
      data:  JSON.stringify(obj),
      success: function( data ) {
//        reload page
      }
    });
}

(function() {
//    console.log( "ready!" );
//    $("#inter_console_table").stupidtable();
});