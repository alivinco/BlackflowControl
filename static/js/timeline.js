/**
 * Created by alivinco on 01/03/15.
 */

var options = {editable: false,maxHeight:"700px"}
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
    data = get_filter()
    $.getJSON('/api/timeseries/timeline',data, function (data) {

        items.clear()
        groups = []
        if(data.length > 0) {
            start_time = data[0].start
            end_time = data[data.length - 1].start

            temp_groups = []
            group_dev_id = []
            for (i in data) {

                if (data[i].content.indexOf("binary") > -1) {
                    data[i]['type'] = 'range'
                } else {
                    data[i]['type'] = 'box'
                }

                data[i]['title'] = data[i].start
                group_name = data[i].address + " " + data[i].content
                dev_id = data[i].dev_id
                if ($.inArray(dev_id,group_dev_id) == -1) {
                    group_dev_id.push(dev_id)
                    temp_groups.push({name:group_name,id:dev_id})
                }
                data[i]['group'] = dev_id
                data[i]['content'] = data[i].value
                items.add(data[i])
            }
            console.dir(temp_groups)
            for (gi in temp_groups) {
                groups.push({id: temp_groups[gi].id, content: temp_groups[gi].name})
            }

            //items.add(events)
            options["start"] = start_time
            options["end"] = end_time
            //console.dir(options)
            timeline.setOptions(options)

        }
            timeline.setGroups(groups)
            timeline.setItems(items)
            //console.dir(groups)
            //console.dir(items)
            //console.log(end_time)


    })
}

function get_filter()
{
    start_time_str = $("#start_time").val();
    stop_time_str =  $("#stop_time").val();
    filter =  $("#filter_field").val();
    limit =  $("#limit").val();
    start_date = (new Date(start_time_str)).getTime()/1000
    stop_date  = (new Date(stop_time_str)).getTime()/1000
    data = {start_dt:start_date,stop_dt:stop_date,filter:filter,limit:limit}
    console.dir(data)
    return data

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
