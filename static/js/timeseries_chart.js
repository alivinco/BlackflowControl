/**
 * Created with PyCharm.
 * User: alivinco
 * Date: 20/08/14
 * Time: 11:36
 * To change this template use File | Settings | File Templates.
 */


$(function () {

    //http://localhost:5000/api/timeseries/get/59/0/2004836694/array

//


    $.getJSON('/api/timeseries/get/'+device_id+'/0/2004836694/array', function (data) {
        // Create the chart
        $('#chart_container').highcharts('StockChart', {


            rangeSelector : {
                selected : 1,
                inputEnabled: $('#chart_container').width() > 480
            },

            title : {
                text : 'Sensor values'
            },

            series : [{
                name : 'Value',
                data : data,
                tooltip: {
                    valueDecimals: 2
                }
            }]
        });
    });




});