/**
 * Created by alivinco on 01/03/15.
 */

var options = {editable: false}
var items = new vis.DataSet()
data = [{content: "SG inclusion",
                id: 1,
                address: "/ta/zw/commands",
                value: 1,
                start: "2014-03-04 15:44:23"}]
//items.add(data)
function loadTimelineData()
{
    $.getJSON('/api/timeseries/timeline/0/2004836694/dict?limit=1000&filter=/22/', function (data) {

        items.clear()
        start_time = data[0].start
        end_time = data[data.length-1].start
        for (i in data) {

            if (data[i].content.indexOf("binary")>-1 ){
                data[i]['type']='box'
            }else
            {
                data[i]['type']='point'
            }
            items.add(data[i])
        }
        console.dir(data)
        console.log(end_time)
        options["start"] = start_time
        options["end"] = end_time
        timeline.setOptions(options)
        //data = [{content: "SG inclusion",
        //        id: 1,
        //        address: "/ta/zw/commands",
        //        value: 1,
        //        start: "2014-08-01"}]
        //items.add(data)
        //timeline.redraw()
        //init_timeline();

    })
}

function init_timeline()
{
    timeline_container = $("#timeline_container")[0];
    console.dir(timeline_container)
    console.dir(items)
    timeline = new vis.Timeline(timeline_container,items,options);
}

$(function(){
    init_timeline()
    loadTimelineData();

    document.getElementById('draw').onclick = loadTimelineData
})
