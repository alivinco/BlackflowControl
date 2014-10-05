/**
 * Created with PyCharm.
 * User: aleksandrsl
 * Date: 27.02.14
 * Time: 15:08
 * To change this template use File | Settings | File Templates.
 */


$(function() {
    load_data()
    if (mode == "normal") start_pooling_cache()
    $("#inter_console_table").stupidtable();
    initi_slider()
});