# V 0.1 2014 , Aleksandrs Livincovs <aleksandrs.livincovs@gmail.com>
# The software is a simple test suite and message repository project for testing Smartly devices .
# The UI is generated based on data extracted from address_mapping.json file and msg_class_mapping.json file
# Message files  have the same name as message class they represent ,
# Command generated based on message template which filled by data generated by user UI , jsonpath is used for
# device field addressing .
# The software provided as is without any support .
# Package dependencies : Flask framework , jsonpath

from flask import Flask, Response, redirect, url_for
from flask import render_template
from flask import request
from modules.mqtt_adapter import MqttAdapter
from modules.msg_cache import MsgCache
from modules.msg_manager import MessageManager
import json
# Flask initialization
from modules.msg_pipeline import MsgPipeline

import configs.log
import logging,logging.config
logging.config.dictConfig(configs.log.config)
log = logging.getLogger("bf_web")


app = Flask(__name__)
msg_man = MessageManager()
cache = MsgCache(msg_man)
# Mqtt initialization
msg_pipeline = MsgPipeline(msg_man,cache)
mqtt = MqttAdapter(msg_pipeline)
mqtt.connect(msg_man.global_configs["mqtt"]["host"],int(msg_man.global_configs["mqtt"]["port"]))
mqtt.sub_topic = msg_man.global_configs["mqtt"]["root_topic"]
mqtt.start()


@app.route('/')
def red():
    return redirect("/ui/inter_console")


@app.route('/sys/mqtt_ctrl/<command>')
def mqtt_control(command):
    if command == "start":
       mqtt.connect(msg_man.global_configs["mqtt"]["host"],int(msg_man.global_configs["mqtt"]["port"]))
       mqtt.sub_topic = msg_man.global_configs["mqtt"]["root_topic"]
       mqtt.start()
       status = "Connected to broker"
    elif command == "stop":
       mqtt.stop()
       status = "Disconnected from broker"

    # dev = json.dumps({"success":True})
    # return Response(response=dev, mimetype='application/json' )
    return render_template('mqtt_status.html', status=status)

@app.route('/ui/inter_console')
def inter_console_ui():
    log.info("Inter console works")
    msg_man.reload_all_mappings()
    mapping = msg_man.generate_linked_mapping(msg_man.load_msg_class_mapping(), msg_man.load_address_mapping())
    return render_template('inter_console.html', mapping=mapping,cache=cache)

@app.route('/ui/address_mapping')
def address_mapping_ui():
    msg_man.reload_all_mappings()

    mapping = msg_man.address_mapping
    # let's add key

    return render_template('address_mapping.html', mapping=mapping)

@app.route('/ui/address_map/<key>')
def address_map_ui(key):
    msg_man.reload_all_mappings()
    mapping = msg_man.get_address_by_key(key)
    if not mapping:
       mapping = {"name":"","key":"","msg_type":"","address":"","msg_class":""}
      # log.info(mapping)

    return render_template('address_map.html', mapping=mapping)


@app.route('/ui/msg_class_mapping')
def msg_class_mapping_ui():
    msg_man.reload_all_mappings()

    mapping = msg_man.msg_class_mapping
    return render_template('msg_class_mapping.html', mapping=mapping)

@app.route('/ui/msg_class/<msg_type>/<msg_class>')
def msg_class_ui(msg_type,msg_class):

    msg_man.reload_all_mappings()
    msg_class_obj = msg_man.get_msg_clas_by_name(msg_type,msg_class)
    try:
        msg_template = json.dumps(msg_man.get_msg_class_template_by_name(msg_type,msg_class),indent=True)
    except Exception as ex:
        log.error("The system can't find the template.")
        log.exception(ex)
        msg_template = "The system can't find the template.Please add template first"
    return render_template('msg_class.html', msg_class=msg_class_obj,msg_template=msg_template)


@app.route('/ui/cache')
def cache_ui():
    # ch = json.dumps(cache.get_all(),indent=True)
    result = {}
    for k,v in cache.get_all().iteritems():
       result[k]=json.dumps(v,indent=True)
    return render_template('cache.html',cache=result)

@app.route('/ui/msg_types_for_approval')
def msg_types_for_approval_ui():
    # cache.put_msg_class_for_approval("test","test","switch_binary_new","Message class is unknown and has to be approved")
    # ch = json.dumps(cache.get_all(),indent=True)
    result = cache.get_approval_list()
    return render_template('msg_types_for_approval.html',cache=result)

@app.route('/ui/settings',methods=["POST","GET"])
def settings_ui():
    if request.method == 'POST':
         msg_man.global_configs["mqtt"]["host"] = request.form["mqtt_host"]
         msg_man.global_configs["mqtt"]["port"] = request.form["mqtt_port"]
         msg_man.global_configs["mqtt"]["root_topic"] = request.form["mqtt_root_topic"]

         f = open(msg_man.global_configs_path,"w")
         f.write(json.dumps(msg_man.global_configs,indent=True))
         f.close()
         log.info("Global config was successfully updated")
         log.info("New values are mqtt host = "+request.form["mqtt_host"]+" port = "+request.form["mqtt_port"]+" root topic = "+request.form["mqtt_root_topic"])

    return render_template('settings.html',cfg=msg_man.global_configs)


@app.route('/api/send_command',methods=["POST"])
def send_command():

    #it has to contain key = switch_binary@.zw.7.binary_switch.2.commands and value
    # 1) load template
    # 2) load msg_class_mapping
    # 3)
    # add to cache
    # format : {"msg_key":"switch_binary@.zw.7.binary_switch.2.commands","user_params":{"value":"True"}}
    log.info("New message from UI")
    try:
        req = request.get_json()
        command = msg_man.generate_command_from_user_params(req["msg_key"],req["user_params"])
        log.debug("Command = "+str(command))
        address = req["msg_key"].split("@")[1]
        log.info("Destination address = "+str(address.replace(".","/")))
        # print json.dumps(command,indent=True
        # mqtt.mqtt.publish(address.replace(".","/"),json.dumps(command),1)
        # cache.put(address,command)
        msg_pipeline.process_command(mqtt,address.replace(".","/"),command)
        dev = json.dumps({"success":True})
    except Exception as ex:
        dev = json.dumps({"success":False})
        log.error("Command can't be sent because of error:")
        log.exception(ex)
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
def approve_msg_class():
    # {"address":address,"msg_class":msg_class,"is_approved":is_approved}

    try:
        req = request.get_json()
        log.info("Msg class for approval , msg class = "+req["msg_class"]+" from address = "+req["address"])

        if req["is_approved"]:
           #adding class
           msg_man.add_msg_class(req["msg_class"],"event")
           #adding address
           msg_man.add_address_to_mapping(req["address"],req["msg_class"])
           # removing the item from approval cache
           approval_key = msg_man.generate_key(req["msg_class"],req["address"])
           msg_man.save_template("event",req["msg_class"],cache.approve_cache[approval_key]["payload"])

           cache.remove_msg_clas_for_approval(approval_key)



        else :
           #TODO:remove the class from approval cache
            log.info("<NOT implemented> the "+req["msg_class"]+" class has to be removed from approval cache")

        dev = json.dumps({"success":True})
    except Exception as ex:
        log.exception(ex)
        dev = json.dumps({"success":False})
    return Response(response=dev, mimetype='application/json' )

@app.route('/api/address_manager',methods=["POST","PUT"])
def address_manager():
    # command should be {"cmd":"remove","address":"/dev/zw/1","msg_class":"thermostat"}
    try:
        if request.method == "PUT":
            req = request.get_json()
            log.info("UI call for address manager . Command = "+req['cmd'])
            if req["cmd"] == "remove":
                msg_man.remove_address_from_mapping(req["address"],req["msg_class"])
            dev = json.dumps({"success":True})
            return Response(response=dev, mimetype='application/json' )
        elif request.method == "POST":
            key = request.form["key"]
            msg_man.update_address_mapping(key,request.form["name"],request.form["msg_class"],request.form["type"],request.form["address"])
            log.info("Address mapping successfully updated")
            return redirect(url_for("address_mapping_ui"))
    except Exception as ex :
        log.exception(ex)



@app.route('/api/get_last_raw_msg/<key>')
def get_last_raw_msg(key):
    result = cache.get_by_key(key)["raw_msg"]
    dev = json.dumps(result)
    return Response(response=dev, mimetype='application/json' )

if __name__ == '__main__':
    app.run(host="0.0.0.0",use_debugger=True,use_reloader=False)
