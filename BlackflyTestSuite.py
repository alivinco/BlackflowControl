# V 0.1 2014 , Aleksandrs Livincovs <aleksandrs.livincovs@gmail.com>
# The software is a simple test suite and message repository project for testing Smartly devices .
# The UI is generated based on data extracted from address_mapping.json file and msg_class_mapping.json file
# Message files  have the same name as message class they represent ,
# Command generated based on message template which filled by data generated by user UI , jsonpath is used for
# device field addressing .
# The software provided as is without any support .
# Package dependencies : Flask framework , jsonpath

from flask import Flask, Response, redirect
from flask import render_template
from flask import request
from modules.mqtt_adapter import MqttAdapter
from modules.msg_cache import MsgCache
from modules.msg_manager import MessageManager
import json
# Flask initialization
from modules.msg_pipeline import MsgPipeline
import configs
import logging,logging.config
from configs import log

logger = logging.getLogger(__name__)
logging.config.dictConfig(log.config)

app = Flask(__name__)
msg_man = MessageManager()
cache = MsgCache(msg_man)
# Mqtt initialization
msg_pipeline = MsgPipeline(msg_man,cache)
mqtt = MqttAdapter(msg_pipeline)
mqtt.connect(configs.app.MQTT_HOST, configs.app.MQTT_PORT)
mqtt.start()


@app.route('/')
def red():
    return redirect("/ui/inter_console")


@app.route('/sys/mqtt_ctrl/<command>')
def mqtt_control(command):
    if command == "start":
       mqtt.start()
    elif command == "stop":
       mqtt.stop()

    dev = json.dumps({"success":True})
    return Response(response=dev, mimetype='application/json' )

@app.route('/ui/inter_console')
def inter_console_ui():
    logging.info("Inter console works")
    msg_man.reload_all_mappings()
    mapping = msg_man.generate_linked_mapping(msg_man.load_msg_class_mapping(), msg_man.load_address_mapping())
    return render_template('inter_console.html', mapping=mapping,cache=cache)

@app.route('/ui/address_mapping')
def address_mapping_ui():
    msg_man.reload_all_mappings()

    mapping = msg_man.address_mapping
    return render_template('address_mapping.html', mapping=mapping)


@app.route('/ui/cache')
def cache_ui():
    # ch = json.dumps(cache.get_all(),indent=True)
    result = {}
    for k,v in cache.get_all().iteritems():
       result[k]=json.dumps(v,indent=True)
    return render_template('cache.html',cache=result)

@app.route('/ui/msg_types_for_approval')
def msg_types_for_approval_ui():
    cache.put_msg_class_for_approval("test","test","switch_binary","Message class is unknown and has to be approved")
    # ch = json.dumps(cache.get_all(),indent=True)
    result = cache.get_approval_list()

    return render_template('msg_types_for_approval.html',cache=result)



@app.route('/api/send_command',methods=["POST"])
def send_command():

    #it has to contain key = switch_binary@.zw.7.binary_switch.2.commands and value
    # 1) load template
    # 2) load msg_class_mapping
    # 3)
    # add to cache
    # format : {"msg_key":"switch_binary@.zw.7.binary_switch.2.commands","user_params":{"value":"True"}}
    req = request.get_json()
    command = msg_man.generate_command_from_user_params(req["msg_key"],req["user_params"])
    address = req["msg_key"].split("@")[1]
    # print json.dumps(command,indent=True
    # mqtt.mqtt.publish(address.replace(".","/"),json.dumps(command),1)
    # cache.put(address,command)
    print "address :"+address
    msg_pipeline.process_command(mqtt,address.replace(".","/"),command)
    dev = json.dumps({"success":True})
    # print request.get_json()
    return Response(response=dev, mimetype='application/json' )

@app.route('/api/get_msg_from_cache/<key>')
def get_msg_from_cache(key="all"):
    #get events from cache
    result = {}
    if key =="all":
        result = cache.get_all()
    else :
        result = cache.get_by_key(key)

    dev = json.dumps({"result":result,"success":True})

    return Response(response=dev, mimetype='application/json' )


@app.route('/api/approve_msg_class',methods=["POST"])
def approve_msg_class(key):
    # {"address":address,"msg_class":msg_class,"is_approved":is_approved}

    req = request.get_json()
    if req["is_approved"]:
       #adding class
       msg_man.add_msg_class(req["msg_class"],req["msg_type"])
       #adding address
       msg_man.add_address_to_mapping(req["address","msg_class"])
       # removing the item from approval cache
       cache.remove_msg_clas_for_approval(msg_man.generate_key(req["msg_class"],req["msg_address"]))
    else :
       #TODO:remove the class from approval cache
        pass

    dev = json.dumps({"success":True})
    return Response(response=dev, mimetype='application/json' )


@app.route('/api/get_last_raw_msg/<key>')
def get_last_raw_msg(key):
    result = cache.get_by_key(key)["raw_msg"]
    dev = json.dumps(result)
    return Response(response=dev, mimetype='application/json' )

if __name__ == '__main__':
    app.run(host="0.0.0.0",use_debugger=True,use_reloader=False)
