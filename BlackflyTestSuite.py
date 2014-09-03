# V 0.1 2014 , Aleksandrs Livincovs <aleksandrs.livincovs@gmail.com>
# The software is a simple test suite and message repository project for testing Smartly devices .
# The UI is generated based on data extracted from address_mapping.json file and msg_class_mapping.json file
# Message files  have the same name as message class they represent ,
# Command generated based on message template which filled by data generated by user UI , jsonpath is used for
# device field addressing .
# The software provided as is without any support .
# Package dependencies : Flask framework , jsonpath

import json
from flask import Flask, Response, redirect, url_for
from flask import render_template
from flask import request
from modules.mod_tools import Tools

from modules.mqtt_adapter import MqttAdapter
from modules.msg_cache import MsgCache
from modules.msg_manager import MessageManager
from modules.dev_simulator import DeviceSimulator

# Flask initialization
from modules.msg_pipeline import MsgPipeline

import configs.log
import logging,logging.config
from configs import mqtt_broker_status_mapping
from modules.mod_timeseries import Timeseries

global_context = {}
logging.config.dictConfig(configs.log.config)
log = logging.getLogger("bf_web")


app = Flask(__name__)
msg_man = MessageManager()

global_context["version"] = msg_man.global_configs["system"]["version"]
cache = MsgCache(msg_man)

timeseries = Timeseries(msg_man.global_configs["db"]["db_path"])
timeseries.init_db()
timeseries.enable(True)
# Mqtt initialization
msg_pipeline = MsgPipeline(msg_man,cache,timeseries)
dev_simulator = DeviceSimulator(msg_man)
mqtt = MqttAdapter(msg_pipeline,msg_man.global_configs["mqtt"]["client_id"])
mqtt.set_mqtt_params(msg_man.global_configs["mqtt"]["client_id"],msg_man.global_configs["mqtt"]["username"],msg_man.global_configs["mqtt"]["password"],msg_man.global_configs["mqtt"]["global_topic_prefix"],msg_man.global_configs["mqtt"]["enable_sys"])
mqtt.sub_topic = msg_man.global_configs["mqtt"]["root_topic"]
mqtt.set_global_context(global_context)
try:
  mqtt.connect(msg_man.global_configs["mqtt"]["host"],int(msg_man.global_configs["mqtt"]["port"]))
  mqtt.start()
except Exception as ex :
  global_context['mqtt_conn_status'] = "offline"
  log.error("application can't connect to message broker.")
  log.error(ex)


@app.route('/')
def red():
    return redirect("/ui/inter_console")


@app.route('/sys/mqtt_ctrl/<command>')
def mqtt_control(command):
    if command == "start":

       try :
         mqtt.connect(msg_man.global_configs["mqtt"]["host"],int(msg_man.global_configs["mqtt"]["port"]))
         mqtt.sub_topic = msg_man.global_configs["mqtt"]["root_topic"]
         mqtt.start()
         status = "Connected to broker"
       except Exception as ex :
         log.error("Can't connect to server because of error:")
         log.error(ex)
         status = "Can't connect to broker"

    elif command == "stop":
       mqtt.stop()
       status = "Disconnected from broker"

    # dev = json.dumps({"success":True})
    # return Response(response=dev, mimetype='application/json' )
    return render_template('mqtt_status.html', status=status,global_context=global_context)

@app.route('/ui/inter_console')
def inter_console_ui():
    log.info("Inter console works")
    filter_value = request.args.get("filter","")
    mode = request.args.get("mode","normal")
    filter_type = request.args.get("filter_type","address")
    log.info(filter_value)
    try :
        #msg_man.reload_all_mappings()
        if mode == "sim" :
            mapping = dev_simulator.get_msg_mapping()
        else :
            mapping = msg_man.generate_linked_mapping(msg_man.load_msg_class_mapping(), msg_man.load_address_mapping())
        if filter_value:
           mapping = filter(lambda item: (filter_value in item["address"]),mapping)
    except Exception as ex :
        log.exception(ex)
    return render_template('inter_console.html', mapping=mapping,cache=cache,global_context=global_context,mode=mode)

@app.route('/ui/dashboard')
def dashboard_ui():
    log.info("Dashboard UI")
    try :
         mapping = msg_man.generate_linked_mapping(msg_man.load_msg_class_mapping(), msg_man.load_address_mapping())
    except Exception as ex :
        log.exception(ex)
    return render_template('dashboard.html', mapping=mapping,cache=cache,global_context=global_context)

@app.route('/ui/mqtt_broker_monitor')
def mqtt_broker_monitor_ui():
    if msg_man.global_configs["mqtt"]["enable_sys"] == True :
        try :
            ch = cache.get_all_generic()
        except Exception as ex :
            log.exception(ex)
        return render_template('mqtt_broker_monitor.html',cache=ch,status_mapping = mqtt_broker_status_mapping,global_context=global_context)
    else :
        status = "Mqtt broker monitoring  is turned off . You can enable it via settings page. "
        return render_template('mqtt_status.html', status=status,global_context=global_context)

@app.route('/ui/address_mapping')
def address_mapping_ui():
    msg_man.reload_all_mappings()

    mapping = msg_man.address_mapping
    # let's add key

    return render_template('address_mapping.html', mapping=mapping,global_context=global_context)

@app.route('/ui/device_templates')
def device_templates_ui():

    mapping = msg_man.address_mapping
    # let's add key

    return render_template('device_templates.html', mapping=mapping,global_context=global_context)


@app.route('/ui/address_map/<key>')
def address_map_ui(key):
    msg_man.reload_all_mappings()
    mapping = msg_man.get_address_by_key(key)
    msg_class_list = msg_man.msg_class_mapping

    if not mapping:
       mapping = {"name":"","key":"","msg_type":"","address":"","msg_class":""}
      # log.info(mapping)

    return render_template('address_map.html', mapping=mapping,msg_class_list=msg_class_list,global_context=global_context)


@app.route('/ui/msg_class_mapping')
def msg_class_mapping_ui():
    msg_man.reload_all_mappings()

    mapping = list(msg_man.msg_class_mapping)

    for item in mapping :
        if "." in item["msg_class"]:
            sp = item["msg_class"].split(".")
            item["class"] = sp[0]
            item["subclass"] = sp[1]
        else :
            item["class"] = ""
            item["subclass"] = item["msg_class"]

    return render_template('msg_class_mapping.html', mapping=mapping,global_context=global_context)

@app.route('/ui/msg_class/<msg_type>/<msg_class>',methods=["POST","GET"])
def msg_class_ui(msg_type,msg_class):
    try:
        if request.method == 'POST':
           class_name = request.form["class"]
           msg_type = request.form["type"]
           msg_class_obj = msg_man.get_msg_clas_by_name(msg_type,class_name)
           ui_el = request.form["ui_element"]
           is_new_class = False

           if not msg_class_obj:
              is_new_class = True
              msg_class_obj = {"ui_mapping": {
                               "ui_element": "",
                               "value_path": ""
                              },
                              "msg_type": "",
                              "msg_class": ""
                             }

           msg_class_obj["ui_mapping"]["ui_element"] = ui_el
           msg_class_obj["ui_mapping"]["value_path"] = request.form["ui_value_path"]
           if ui_el == "sensor_value":
              um = msg_class_obj["ui_mapping"]
              um["unit_path"] = request.form["ui_unit_path"]
           elif ui_el == "input_num_field":
              msg_class_obj["ui_mapping"]["num_type"] = request.form["ui_num_type"]

           if is_new_class:
              log.info("Adding new message class to mapping ; "+str(msg_class_obj))
              msg_man.msg_class_mapping.append(msg_class)
           else:
              log.info("Updating class mapping "+str(msg_class_obj))

           msg_man.serialize_class_mapping()
        else :
           msg_man.reload_all_mappings()

    except Exception as ex :
        log.error(ex)

    msg_class_obj = msg_man.get_msg_clas_by_name(msg_type,msg_class)

    try:
        msg_template = json.dumps(msg_man.get_msg_class_template_by_name(msg_type,msg_class),indent=True)
    except Exception as ex:
        log.error("The system can't find the template.")
        log.exception(ex)
        msg_template = "The system can't find the template.Please add template first"
    return render_template('msg_class.html', msg_class=msg_class_obj,msg_template=msg_template,global_context=global_context)


@app.route('/ui/cache')
def cache_ui():
    # ch = json.dumps(cache.get_all(),indent=True)
    result = {}
    for k,v in cache.get_all().iteritems():
       result[k]=json.dumps(v,indent=True)
    return render_template('cache.html',cache=result,global_context=global_context)

@app.route('/ui/timeseries/chart/<dev_id>')
def timeseries_chart(dev_id):
    # ch = json.dumps(cache.get_all(),indent=True)
    result = {}
    device_info = {"device_id":dev_id}
    return render_template('timeseries_chart.html',cache=result,global_context=global_context,device_info=device_info)

@app.route('/ui/timeseries/table/<dev_id>/<start_time>/<end_time>')
def timeseries_table(dev_id,start_time,end_time):
    # ch = json.dumps(cache.get_all(),indent=True)
    result = timeseries.get(dev_id,start_time,end_time)
    return render_template('timeseries_table.html',ts=result,global_context=global_context)

@app.route('/ui/msg_types_for_approval')
def msg_types_for_approval_ui():
    # cache.put_msg_class_for_approval("test","test","switch_binary_new","Message class is unknown and has to be approved")
    # ch = json.dumps(cache.get_all(),indent=True)
    result = cache.get_approval_list()
    return render_template('msg_types_for_approval.html',cache=result,global_context=global_context)

@app.route('/ui/settings',methods=["POST","GET"])
def settings_ui():
    if request.method == 'POST':
         msg_man.global_configs["mqtt"]["host"] = request.form["mqtt_host"]
         msg_man.global_configs["mqtt"]["port"] = request.form["mqtt_port"]
         msg_man.global_configs["mqtt"]["root_topic"] = request.form["mqtt_root_topic"]
         msg_man.global_configs["mqtt"]["client_id"] = request.form["mqtt_client_id"]
         msg_man.global_configs["mqtt"]["username"] = request.form["mqtt_username"]
         msg_man.global_configs["mqtt"]["password"] = request.form["mqtt_password"]
         msg_man.global_configs["mqtt"]["global_topic_prefix"] = request.form["mqtt_global_topic_prefix"]
         if request.form["enable_sys"] == "True":
            msg_man.global_configs["mqtt"]["enable_sys"] = True
         else :
            msg_man.global_configs["mqtt"]["enable_sys"] = False

         msg_man.global_configs["db"]["db_path"] = request.form["db_path"]
         mqtt.set_mqtt_params(request.form["mqtt_client_id"],request.form["mqtt_username"],request.form["mqtt_password"],request.form["mqtt_global_topic_prefix"],msg_man.global_configs["mqtt"]["enable_sys"])

         f = open(msg_man.global_configs_path,"w")
         f.write(json.dumps(msg_man.global_configs,indent=True))
         f.close()
         log.info("Global config was successfully updated")
         log.info("New values are mqtt host = "+request.form["mqtt_host"]+" port = "+request.form["mqtt_port"]+" root topic = "+request.form["mqtt_root_topic"]+" client id="+request.form["mqtt_client_id"])

    return render_template('settings.html',cfg=msg_man.global_configs,global_context=global_context)


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
        log.debug("Command message = "+str(command))
        address = req["msg_key"].split("@")[1]
        log.info("Destination address = "+str(address.replace(".","/"))+"; Mode = "+req["mode"])
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
    error_msg = ""
    try:
        if request.method == "PUT":
            req = request.get_json()
            log.info("UI call for address manager . Command = "+req['cmd'])
            if req["cmd"] == "remove":
                addr_id = int(req["id"])
                msg_man.remove_address_from_mapping(addr_id)
                timeseries.delete_all_for_dev(addr_id)

            dev = json.dumps({"success":True})
            return Response(response=dev, mimetype='application/json' )
        elif request.method == "POST":
            action = request.form["action"]

            if action == "update_address_mapping":
                key = request.form["key"]
                override_props = ""
                override_value_path = ""
                try:
                  if request.form["override_properties"] != "None" and request.form["override_properties"]!= "":
                   override_props = json.loads(request.form["override_properties"])
                  override_value_path = request.form["override_value_path"]
                except:
                  error_msg = "Override properties is not a json object,therefore it will be skipped"
                  log.error(error_msg)


                msg_man.update_address_mapping(key,request.form["name"],request.form["msg_class"],request.form["type"],request.form["address"],override_props,override_value_path)
                log.info("Address mapping successfully updated")
            elif action =="bulk_address_update":
                msg_man.find_replace_address(request.form["find"],request.form["replace_to"])
                log.info("Address mapping successfully updated by find_replace_address")
            elif action =="bulk_address_delete":
                ids_list = msg_man.bulk_address_removal(request.form["find"])
                timeseries.delete_all_for_dev(ids_list)
                log.info("Bulk delete was completed.")
            return redirect(url_for("address_mapping_ui"))
    except Exception as ex :
        log.exception(ex)
        return redirect(url_for("address_mapping_ui"))



@app.route('/api/get_last_raw_msg/<key>')
def get_last_raw_msg(key):
    try:
        result = cache.get_by_key(key)["raw_msg"]
        dev = json.dumps(result)
    except :
        dev = {"error":"The message not found.Perhaps it has never been captured by the system"}
    return Response(response=dev, mimetype='application/json')

@app.route('/api/timeseries/get/<dev_id>/<start>/<end>/<result_type>')
def get_timeseries(dev_id,start,end,result_type):
    ts = timeseries.get(int(dev_id),int(start),int(end),result_type)
    jobj = json.dumps(ts)
    return Response(response=jobj, mimetype='application/json')


@app.route('/ui/help/<page>')
def help(page):
    return render_template('help_'+page+'.html',cfg=msg_man.global_configs,global_context=global_context)

@app.route('/ui/dr_browser')
def dr_browser():

    return render_template('dr_device_browser.html',global_context=global_context)

@app.route('/ui/tools',methods=["POST","GET"])
def tools():
    tools = Tools()
    output = ""
    try:
        if request.method == "POST":
            action = request.form["action"]
            if action == "start_service":
                service_name = request.form["service_name"]
                output = tools.start_service(service_name)
            elif action == "stop_service":
                service_name = request.form["service_name"]
                output = tools.stop_service(service_name)
            elif action == "query_status":
                service_name = request.form["service_name"]
                output = tools.process_status(service_name)
            elif action == "tail_log":
                log_file = request.form["log_file"]
                tail_size = request.form["tail_size"]
                output = tools.tail_log(log_file,int(tail_size))

        else :
            pass
    except Exception as ex :
        output = str(ex)


    return render_template('tools.html',output=output ,global_context=global_context)



if __name__ == '__main__':
    app.run(host="0.0.0.0",use_debugger=False,threaded=True,use_reloader=False)
