/**
 * Created with PyCharm.
 * User: aleksandrsl
 * Date: 02.04.14
 * Time: 15:02
 * To change this template use File | Settings | File Templates.
 */

function syntaxHighlight(json) {
    if (typeof json != 'string') {
         json = JSON.stringify(json, undefined, 2);
    }
    json = json.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    return json.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g, function (match) {
        var cls = 'number';
        if (/^"/.test(match)) {
            if (/:$/.test(match)) {
                cls = 'key';
            } else {
                cls = 'string';
            }
        } else if (/true|false/.test(match)) {
            cls = 'boolean';
        } else if (/null/.test(match)) {
            cls = 'null';
        }
        return '<span class="' + cls + '">' + match + '</span>';
    });
}
function guidGen() {
  var d = new Date().getTime();
    var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = (d + Math.random()*16)%16 | 0;
        d = Math.floor(d/16);
        return (c=='x' ? r : (r&0x3|0x8)).toString(16);
    });
    return uuid;
}

function getMessagePacket(msg_type,msg_class,msg_subclass)
{
    guid = guidGen()

    template =  {
         origin: {
          "@id": "blackfly",
          vendor: "blackfly",
          "@type": "app"
         },
         uuid:guid,
         creation_time: new Date().getTime(),
         spid: ""
        }
    template[msg_type]={
         "subtype": msg_subclass,
         "@type": msg_class,
         "default":{"value":""},
         "properties":{}
         }
    console.dir(template)
    return template
}

function convertDictToKeyValList(dict)
{
    result = []
    for (k in dict)
    {result.push({"key":k,"value":dict[k]})}
    return result
}
function convertKeyValueListToDict(list)
{
    result = {}
    for(item in list)
    {
        result[list[item].key] = list[item].value
    }
    return result
}

function convertListToKeyValueList(simple_list)
{
    result = []
    for (k in simple_list)
    {result.push({"value":simple_list[k]})}
    return result

}
function convertKeyValueListToList(klist)
{
    result = []
    for(item in klist)
    {
        result.push(klist[item].value)
    }
    return result
}