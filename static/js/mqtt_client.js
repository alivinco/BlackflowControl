/**
 * Created by alivinco on 28/08/15.
 */

function send_message()
  {
      data = {"address":$("#inputAddress").val(),"payload":$("#payload").val()}
      $.post( "/ui/mqtt_client",data, function( data ) {
          console.log("Message was sent")
          resend_delay = parseInt($("#inputAutoresendDelay").val())
          if (resend_delay > 0) {
              setTimeout(send_message, resend_delay);
          }
        });



  }