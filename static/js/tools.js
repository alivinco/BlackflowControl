/**
 * Created with PyCharm.
 * User: alivinco
 * Date: 04/09/14
 * Time: 17:21
 * To change this template use File | Settings | File Templates.
 */


function load_logs()
{
    console.log("submitting form")

    $.post( root_uri+"/ui/logviewer", $( "#log_viewer_form" ).serialize(),function(data){
        console.log("ok")
        $("#log_output").html(data)
    } );

//$("#log_viewer_form")[0].submit(function() {
//
//    var url = "/ui/logviewer"; // the script where you handle the form input.
//    console.log("submitting form")
//    $.ajax({
//           type: "POST",
//           url: url,
//           data: $("#log_viewer_form").serialize(), // serializes the form's elements.
//           success: function(data)
//           {
//               alert(data); // show response from the php script.
//           }
//         });
//
//    return false; // avoid to execute the actual submit of the form.
//});

}


$(function() {

})