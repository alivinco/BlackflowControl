/**
 * Created by alivinco on 01/03/15.
 */

var options = {editable: false}
var items = new vis.DataSet()

var groups = []


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

        temp_groups = []
        for (i in data) {

            if (data[i].content.indexOf("binary")>-1 ){
                data[i]['type']='range'
            }else
            {
                data[i]['type']='box'
            }

            data[i]['title'] = data[i].start

            if (temp_groups.indexOf(data[i].content) == -1 )
            {

                temp_groups.push(data[i].content)
            }
            data[i]['group']=data[i].content
            data[i]['content'] = data[i].value
            items.add(data[i])
        }

        for (gi in temp_groups)
        {
            groups.push({id:temp_groups[gi],content:temp_groups[gi]})
        }

        //items.add(events)

        timeline.setGroups(groups)
        timeline.setItems(items)
        console.dir(groups)
        console.dir(items)
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
    //console.dir(timeline_container)
    //console.dir(items)
    timeline = new vis.Timeline(timeline_container);
}

$(function(){
    init_timeline()
    loadTimelineData();

    document.getElementById('draw').onclick = loadTimelineData
})
