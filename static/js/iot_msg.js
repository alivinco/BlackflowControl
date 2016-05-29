/**
 * Created by alivinco on 29/05/16.
 */

function IotMsg(origin, msg_type, msg_class, msg_subclass, timestamp, uuid_, corid, req_msg)
{
    this.origin = origin
    this.msg_type = msg_type
    this.msg_class = msg_class
    this.msg_subclass = msg_subclass
    this.default = None
    this.properties = None
    this.topic = None
    this.timestamp = timestamp
    this.uuid = uuid_
    this.corid = corid
    if (req_msg) {
        this.corid = req_msg.get_uuid()
    }

    this.setDefault = function(value, unit, type_){
        v = {"value":value}
        if (unit) {
            v["unit"] = unit
        }
        if (type_) {
            v["type"] = type_
        }
        this.default = v
    }

    this.getDefault = function (){
        return this.default
    }

    this.setProperties = function (props){
        this.properties = props
    }

    this.getProperties = function(){
        return this.properties
    }


}