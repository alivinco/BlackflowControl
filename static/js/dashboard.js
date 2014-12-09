/**
 * Created with PyCharm.
 * User: alivinco
 * Date: 18/09/14
 * Time: 16:42
 * To change this template use File | Settings | File Templates.
 */
//$(function() {
//    $( ".row" ).sortable({
//      connectWith: ".row",
//      handle: ".panel-heading",
//      items:".col-sm-2",
//      cursor: "move"
////      cancel: ".portlet-toggle",
////      placeholder: "portlet-placeholder ui-corner-all"
//    });
//
//
//  });

function dashboard_api(data)
{
    $.ajax({
      url: "/api/dashboard",
      type: 'POST',
//      contentType: 'application/json; charset=utf-8',
      data: data,
      success: function( data ) {
       console.log("Dash api success")
      }
    });

}

function init_dnd_handler()
{

    var boxes_ = document.querySelectorAll('.movable');
    var dragSrcEl_ = null;
    this.handleDragStart = function (e) {
        e.dataTransfer.effectAllowed = 'move';
        e.dataTransfer.setData('text/html', this.innerHTML);
        dragSrcEl_ = this;
        this.style.opacity = '0.5';
        // this/e.target is the source node.
//        console.dir(this)
//        this.addClassName('moving');
    };
    this.handleDragOver = function (e) {
        if (e.preventDefault) {
            e.preventDefault(); // Allows us to drop.
        }
        e.dataTransfer.dropEffect = 'move';
        return false;
    };
    this.handleDragEnter = function (e) {
//        this.addClassName('over');
    };
    this.handleDragLeave = function (e) {
        // this/e.target is previous target element.
//        this.removeClassName('over');
    };
    this.handleDrop = function (e) {
        // this/e.target is current target element.

        if (e.stopPropagation) {
            e.stopPropagation(); // stops the browser from redirecting.
        }
        // Don't do anything if we're dropping on the same box we're dragging.
        if (dragSrcEl_ != this) {

            dragSrcEl_.innerHTML = this.innerHTML;
            this.innerHTML = e.dataTransfer.getData('text/html');
        }
//        console.dir($(this).children('.movable_div'))
//        console.dir(dragSrcEl_)
        source_element_id = $(this).children('.movable_div')[0].id;
        target_element_id = $(dragSrcEl_).children('.movable_div')[0].id;

        source_div_id_parsed = source_element_id.split("_")
        start_group_id = source_div_id_parsed[1]
        source_dev_id = source_div_id_parsed[2]
        source_location = source_div_id_parsed[3]+"_"+source_div_id_parsed[4]

        target_div_id_parsed = target_element_id.split("_")
        dest_group_id = target_div_id_parsed[1]
        target_dev_id = target_div_id_parsed[2]
        target_location = target_div_id_parsed[3]+"_"+target_div_id_parsed[4]

        // Swaping div Id's location parts , location part should be always the same
        $(this).children('.movable_div')[0].id = "panel_"+start_group_id+"_"+source_dev_id+"_"+target_location
        $(dragSrcEl_).children('.movable_div')[0].id = "panel_"+dest_group_id+"_"+target_dev_id+"_"+source_location

        console.log("Moving panel from "+source_location+" to "+target_location)

        console.log("Moving moving from  :"+source_element_id)
        console.log("Moving moving to  :"+target_element_id)

        source_pos = source_location.split("_")
        target_pos = target_location.split("_")

        movable_service_id=source_dev_id
        drop_service_id=target_dev_id
        start_x_position=source_pos[0]
        start_y_position=source_pos[1]
        dest_x_position=target_pos[0]
        dest_y_position=target_pos[1]
//        start_group_id=
//        dest_group_id
        if (drop_service_id=="null") drop_service_id = ""
        data = {"action":"change_service_position",
                "movable_service_id":movable_service_id,
                "drop_service_id":drop_service_id,
                "start_x_position":start_x_position,
                "start_y_position":start_y_position,
                "dest_x_position":dest_x_position,
                "dest_y_position":dest_y_position,
                "start_group_id":start_group_id,
                "dest_group_id":dest_group_id,
                "dashboard_id":dashboard_id
        }
        dashboard_api(data)

        return false;
    };
    this.handleDragEnd = function (e) {
        // this/e.target is the source node.
        this.style.opacity = '1';

//        [ ].forEach.call(boxes_, function (box) {
//            box.removeClassName('over');
//            box.removeClassName('moving');
//        });
    };

    [ ].forEach.call(boxes_, function (box) {
        box.setAttribute('draggable', 'true');  // Enable boxes to be draggable.
        box.addEventListener('dragstart', this.handleDragStart, false);
        box.addEventListener('dragenter', this.handleDragEnter, false);
        box.addEventListener('dragover', this.handleDragOver, false);
        box.addEventListener('dragleave', this.handleDragLeave, false);
        box.addEventListener('drop', this.handleDrop, false);
        box.addEventListener('dragend', this.handleDragEnd, false);
    });

}


$(function() {
  init_dnd_handler()

  load_data()
  start_pooling_cache()
  initi_slider()
});