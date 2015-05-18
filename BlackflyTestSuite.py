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
import time
import libs
from libs.dmapi.core import Core
from libs.flask_login import LoginManager, login_required
from mappings.msg_class_to_zw import get_msg_class_by_capabilities
import modules
from modules.mod_dashboards import DashboardManager
from modules.mod_filters import FiltersManager
from modules.mod_tools import Tools
from modules.mod_zwave_tools import ZwaveTools

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
import re

from libs.sync_to_async_msg_converter import SyncToAsyncMsgConverter

from libs.dmapi import devicereg,zw_ta

from modules.mod_auth import login_manager , mod_auth
import modules.mod_auth


global_context = {}
logging.config.dictConfig(configs.log.config)
log = logging.getLogger("bf_web")
log.info("Checking firewall configuration")
log.info(Tools.open_port_in_firewall())
msg_man = MessageManager()
# Flask init
app = Flask(__name__)
app.secret_key = '\x94&J\x8f\xe2+\x93Hr\xdd\xb8\x15./\xd0\x13\xf0\x88\x15f\x8f`\xec\xcd'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = '/tmp/'
app.config['LOGIN_DISABLED'] = msg_man.global_configs["system"]["ui_security_disabled"]
app.register_blueprint(mod_auth)

login_manager.init_app(app)

modules.mod_auth.global_context = global_context


global_context["version"] = msg_man.global_configs["system"]["version"]
http_server_port = msg_man.global_configs["system"]["http_server_port"]
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

sync_async_client = SyncToAsyncMsgConverter(mqtt)
msg_pipeline.set_sync_async_client(sync_async_client)

dash_man = DashboardManager()
filter_man = FiltersManager()

zwapi = zw_ta.ZwTa("app","blackfly","blackfly")
deviceregapi = devicereg.Devicereg("app","blackfly","blackfly")

@app.route('/')
def red():
    return redirect("/ui/inter_console")


@app.route('/sys/mqtt_ctrl/<command>')
@login_required
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
@login_required
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
            mapping = msg_man.generate_linked_mapping(msg_man.msg_class_mapping, msg_man.address_mapping)
        if filter_value:
           p = re.compile(filter_value,re.IGNORECASE)
           mapping = filter(lambda item: (p.search(item["address"])),mapping)

        saved_filters = filter_man.get_filters("inter_console")

    except Exception as ex :
        log.exception(ex)
    return render_template('inter_console.html', mapping=mapping,cache=cache,global_context=global_context,mode=mode,filter_value=filter_value,saved_filters=saved_filters)

@app.route('/ui/dashboard/<dash_name>')
@login_required
def dashboard_ui(dash_name):
    log.info("Dashboard UI")
    try :
         dash_man.load_dashboard_map()
         mapping = msg_man.generate_linked_mapping(msg_man.msg_class_mapping, msg_man.address_mapping)
         ext_mapping = dash_man.get_extended_dashboard_map(dash_name,mapping)
         # dash_map = dash_man.get_dashboard_map(dash_name)
         address_list = msg_man.address_mapping
         # grid_size = dash_man.get_dashboard_grid_size(dash_name)
         groups = dash_man.get_dashboard_map(dash_name)["groups"]
         log.info(groups)
    except Exception as ex :
        log.exception(ex)
    return render_template('dashboard.html',dashboard_id = dash_name, mapping=ext_mapping,address_list=address_list,groups=groups,cache=cache,global_context=global_context)

@app.route('/ui/mqtt_broker_monitor')
@login_required
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
@login_required
def address_mapping_ui():
    msg_man.reload_all_mappings()

    mapping = msg_man.address_mapping
    # let's add key

    return render_template('address_mapping.html', mapping=mapping,global_context=global_context)

@app.route('/ui/device_templates')
@login_required
def device_templates_ui():

    mapping = msg_man.address_mapping
    # let's add key

    return render_template('device_templates.html', mapping=mapping,global_context=global_context)


@app.route('/ui/address_map/<key>')
@login_required
def address_map_ui(key):
    msg_man.reload_all_mappings()
    mapping = msg_man.get_address_by_key(key)
    msg_class_list = msg_man.msg_class_mapping

    if not mapping:
       mapping = {"name":"","key":"","msg_type":"","address":"","msg_class":""}
      # log.info(mapping)

    return render_template('address_map.html', mapping=mapping,msg_class_list=msg_class_list,global_context=global_context)


@app.route('/ui/msg_class_mapping')
@login_required
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
@login_required
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
@login_required
def cache_ui():
    # ch = json.dumps(cache.get_all(),indent=True)
    result = {}
    for k,v in cache.get_all().iteritems():
       result[k]=json.dumps(v,indent=True)
    return render_template('cache.html',cache=result,global_context=global_context)

@app.route('/ui/timeseries/chart/<dev_id>')
@login_required
def timeseries_chart(dev_id):
    # ch = json.dumps(cache.get_all(),indent=True)
    result = {}
    device_info = {"device_id":dev_id}
    return render_template('timeseries_chart.html',cache=result,global_context=global_context,device_info=device_info)

@app.route('/ui/timeseries/table/<dev_id>/<start_time>/<end_time>',methods=["POST","GET"])
@login_required
def timeseries_table(dev_id,start_time,end_time):
    # ch = json.dumps(cache.get_all(),indent=True)
    if request.method == "POST":
        action = request.form["action"]
        if action == "delete_all":
            timeseries.delete_all_for_dev(int(dev_id))
            log.info("All lot items for device with id = %s were deleted"%dev_id)

    result = timeseries.get(dev_id,start_time,end_time)
    device_info = {"device_id":dev_id}
    return render_template('timeseries_table.html',ts=result,global_context=global_context,device_info=device_info)

@app.route('/ui/timeseries/timeline/<start_time>/<end_time>',methods=["POST","GET"])
@login_required
def timeseries_timeline(start_time,end_time):
    # ch = json.dumps(cache.get_all(),indent=True)
    if request.method == "POST":
        action = request.form["action"]
        if action == "delete_all":
            timeseries.delete_all_for_dev(int(dev_id))
            log.info("All lot items for device with id = %s were deleted"%dev_id)

    return render_template('timeseries_timeline.html',global_context=global_context)


@app.route('/ui/msg_types_for_approval')
@login_required
def msg_types_for_approval_ui():
    # cache.put_msg_class_for_approval("test","test","switch_binary_new","Message class is unknown and has to be approved")
    # ch = json.dumps(cache.get_all(),indent=True)
    result = cache.get_approval_list()
    return render_template('msg_types_for_approval.html',cache=result,global_context=global_context)

@app.route('/ui/settings',methods=["POST","GET"])
@login_required
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

         msg_man.serialize_global_config()

         log.info("Global config was successfully updated")
         log.info("New values are mqtt host = "+request.form["mqtt_host"]+" port = "+request.form["mqtt_port"]+" root topic = "+request.form["mqtt_root_topic"]+" client id="+request.form["mqtt_client_id"])

    return render_template('settings.html',cfg=msg_man.global_configs,global_context=global_context)


@app.route('/api/send_command',methods=["POST"])
@login_required
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
        result = cache.get_all(exclude_raw_msg=True)
    else :
        result = cache.get_by_key(key)

    dev = json.dumps({"result":result,"success":True})

    return Response(response=dev, mimetype='application/json' )


@app.route('/api/approve_msg_class',methods=["POST"])
@login_required
def approve_msg_class():
    # {"address":address,"msg_class":msg_class,"is_approved":is_approved}

    try:
        req = request.get_json()
        log.info("Msg class for approval , msg class = "+req["msg_class"]+" from address = "+req["address"])

        if req["is_approved"]:

           if "event" in req["address"]:
             msg_type = "event"
           else:
             msg_type = "command"

           #adding class
           msg_man.add_msg_class(req["msg_class"],msg_type)
           #adding address
           msg_man.add_address_to_mapping(req["address"],req["msg_class"])
           # removing the item from approval cache
           approval_key = msg_man.generate_key(req["msg_class"],req["address"])
           msg_man.save_template(msg_type,req["msg_class"],cache.approve_cache[approval_key]["payload"])

           cache.remove_msg_clas_for_approval(approval_key)

        else :
            log.info("Msg will be removed "+req["msg_class"]+" class has to be removed from approval cache")
            approval_key = msg_man.generate_key(req["msg_class"],req["address"])
            cache.remove_msg_clas_for_approval(approval_key)

        dev = json.dumps({"success":True})
    except Exception as ex:
        log.exception(ex)
        dev = json.dumps({"success":False})
    return Response(response=dev, mimetype='application/json' )

@app.route('/api/address_manager',methods=["POST","PUT"])
@login_required
def address_manager():
    # command should be {"cmd":"remove","address":"/dev/zw/1","msg_class":"thermostat"}
    """
    Address manager . It exposes rest api for manipulating with service-address mappings .

    :return:
    """
    error_msg = ""
    try:
        if request.method == "GET":
            # adding address based on dev_type and capability
            action = request.args.get("action","")
            if action == "add_address_using_dev_type":
                dev_type = request.args.get("dev_type","")
                capability = request.args.get("capability","")
                address = request.args.get("address","")
                msg_classes_list = get_msg_class_by_capabilities(dev_type,capability)
                for item in msg_classes_list:
                    log.info("Msg class is recognized as :"+str(item.msg_class))
                    msg_man.add_address_to_mapping(address,item.msg_class)
                return redirect(url_for("inter_console_ui",filter=address,mode="normal"))

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

                msg_class_split = request.form["msg_class"].split("->")
                msg_type = msg_class_split[0]
                msg_class = msg_class_split[1]
                str_to_bool = {"True":True,"False":False}
                record_history = str_to_bool[request.form["record_history"]]
                msg_man.update_address_mapping(key,request.form["name"],msg_class,msg_type,request.form["address"],override_props,override_value_path,record_history)
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

@app.route('/api/filters',methods=["POST","GET"])
@login_required
def filters_api():

    """
    Ineteractive console filters api .

    :return:
    """
    if request.method == "POST":
       action = request.form["action"]
    elif request.method == "GET":
       action = request.args.get("action","")
    else :
       action = ""

    if action =="upsert":
       name = request.form["name"]
       filter = request.form["filter"]
       filter_man.upsert_filter("inter_console",None,name,filter)
    elif action =="delete":
       id = int(request.args.get("id",""))

       filter_man.delete_filter("inter_console",id)

    return redirect(url_for("inter_console_ui"))

@app.route('/api/dashboard',methods=["POST","GET"])
@login_required
def dashboard_api():

    """
    REST api for creating and managing dashboards.

    :return:
    """
    if request.method == "POST":
       action = request.form["action"]
       log.info("Dashboard api action = "+action)
       dashboard_id = request.form["dashboard_id"]

    if action :
         if action == "add_service_to_dashboard":
             service_id = request.form["service_id"]
             group_id = int(request.form["group_id"])
             service_name = request.form["service_name"]
             position_y = request.form["position_y"]
             position_x = request.form["position_x"]
             dash_man.add_service_to_dashboard(dashboard_id,group_id,service_id,position_x,position_y,service_name)
         elif action == "delete_service_from_dashboard":
             service_id = request.form["service_id"]
             dash_man.delete_service_from_dashboard(dashboard_id,service_id)
         elif action == "update_service":
             service_id = request.form["service_id"]
             service_name = request.form["service_name"]
             dash_man.update_service(dashboard_id,service_id,service_name)
         elif action == "update_group":
             group_id = int(request.form["group_id"])
             group_name = request.form["group_name"]
             x_size = int(request.form["group_x_size"])
             y_size = int(request.form["group_y_size"])
             dash_man.update_group(dashboard_id,group_id,x_size,y_size,group_name)
         elif action == "delete_group_from_dashboard":
             log.info("Deleting group from dashboard")
             group_id = int(request.form["group_id"])
             dash_man.delete_group(dashboard_id,group_id)
         elif action == "change_service_position":
             log.info("Changing service position...")
             dash_man.change_service_position(dashboard_id,
                                              movable_service_id=request.form["movable_service_id"],
                                              drop_service_id=request.form["drop_service_id"],
                                              start_x_position=int(request.form["start_x_position"]),
                                              start_y_position=int(request.form["start_y_position"]),
                                              dest_x_position=int(request.form["dest_x_position"]),
                                              dest_y_position=int(request.form["dest_y_position"]),
                                              start_group_id=int(request.form["start_group_id"]),
                                              dest_group_id=int(request.form["dest_group_id"]))

    return redirect(url_for("dashboard_ui",dash_name=dashboard_id))


@app.route('/api/msg_history',methods=["POST"])
@login_required
def msg_history_api():
    log.info("Msg history API")
    try:
        if request.method == "POST":
           action = request.form["action"]
           id = int(request.form["id"])

        if action =="resend":
            msg = timeseries.get_msg_history(rowid=id)[0]
            log.info(msg)
            mqtt.publish(msg["address"],msg["msg"],1)
        elif action =="delete":
            timeseries.delete_msg_history("rowid",id)
    except Exception as ex:
        log.error(ex)

    return redirect(url_for("msg_history"))

@app.route('/api/get_last_raw_msg/<key>')
@login_required
def get_last_raw_msg(key):
    try:
        result = cache.get_by_key(key)["raw_msg"]
        dev = json.dumps(result)
    except :
        dev = {"error":"The message not found.Perhaps it has never been captured by the system"}
    return Response(response=dev, mimetype='application/json')

@app.route('/api/timeseries/get/<dev_id>/<start>/<end>/<result_type>')
@login_required
def get_timeseries(dev_id,start,end,result_type):
    ts = timeseries.get(int(dev_id),int(start),int(end),result_type)
    jobj = json.dumps(ts)
    return Response(response=jobj, mimetype='application/json')

@app.route('/api/timeseries/timeline')
@login_required
def get_timeline():
    log.info("Timeline request")

    if request.method == "GET":
            # adding address based on dev_type and capability
            # TODO: something wrong with timezones , in db time is stored in GMT and request is in local time .
            try:
                start = int(request.args.get("start_dt",""))
                stop  = int(request.args.get("stop_dt",""))
            except:
                stop  = int(time.time())
                start = int(stop - 3600)

            log.info("Start time = %s stopt time = %s"%(start,stop))
            filter  = request.args.get("filter","")

            limit = request.args.get("limit","100")
            result_type = "dict"

            ts = timeseries.get_timeline(msg_man.address_mapping,filter,start,stop,int(limit),result_type)
    jobj = json.dumps(ts)
    return Response(response=jobj, mimetype='application/json')


@app.route('/ui/help/<page>')
@login_required
def help(page):
    return render_template('help_'+page+'.html',cfg=msg_man.global_configs,global_context=global_context)

@app.route('/ui/dr_browser',methods=["GET","POST"])
@login_required
def dr_browser():
    log.info("Device registry browser")
    if request.method == "POST":
        action = request.form["action"]
        device_id = int(request.form["device_id"])
        field_name = request.form["field_name"]
        field_value = request.form["field_value"]
        msg = deviceregapi.update({"Id":device_id},{field_name:field_value})
        log.info(msg)
        response = sync_async_client.send_sync_msg(msg,"/app/devicereg/commands","/app/devicereg/events",timeout=10)

    msg = deviceregapi.get_device_list()
    # log.debug(msg)
    response = sync_async_client.send_sync_msg(msg,"/app/devicereg/commands","/app/devicereg/events",timeout=5)
    log.debug("response :"+str(response))
    # response = None
    if not response :
            log.warn("Deviceregistry is not responding therefore loading STATIC message template")
            response = Core().load_template("event","devicereg.device_list")
    return render_template('dr_device_browser.html',dr_response=response,global_context=global_context,configs = msg_man.global_configs)

@app.route('/ui/zw_diagnostics')
@login_required
def zw_diagnostics():
    log.info("Zw diagnostics")
    action = request.args.get("action","")
    # get routing info may take some time to generate the response for zwave stack , therefore it may be usefull to show values from cache and add
    # refresh on demand feature .
    response = cache.get("zw_ta.routing_info","/ta/zw/events")
    if action == "refresh_routing_info" or not response :
        log.info("Doing zwave info refresh")
        msg = zwapi.get_routing_info()
        # That is propper request
        response = sync_async_client.send_sync_msg(msg,"/ta/zw/commands","/ta/zw/events",correlation_type="MSG_TYPE",correlation_msg_type="zw_ta.routing_info")
        # This 2 lines below are a workaround while zwave ta is not available
        # response  = json.load(file("tests/poc/network_info.json"))
        if not response : response  = {"event":{"properties":{}}}
        cache.put("zw_ta.routing_info@.ta.zw.events",response,{"ui_element":{}},{})

    else :
        response = response["raw_msg"]

    routing_info = response["event"]["properties"]

    log.debug("response :"+str(response))
    return render_template('zw_diagnostics.html',routing_info=routing_info,global_context=global_context)


#TODO: That part is depricated and have to be removed .
# @app.route('/api/zw_diagnostics/<action>')
# def zw_diagnostics_api(action):
#     if action == "get_network_graph":
#         # getting network infor from cache
#         response = cache.get("zw_ta.routing_info","/ta/zw/events")
#         routing_info = response["raw_msg"]["event"]["properties"]
#         graph = ZwaveTools().get_network_graph(routing_info)
#         jobj = json.dumps(graph)
#     else :
#         jobj = json.dumps({})
#     return Response(response=jobj, mimetype='application/json')

@app.route('/api/zw_manager',methods=["POST"])
@login_required
def zw_manager_api():
    action = request.form["action"]
    log.debug("Action"+action)
    if action == "zw_inclusion_mode":
        log.info("Setting zwave controller into inclusion mode")
        start =  libs.utils.convert_bool(request.form["start"])
        msg = zwapi.inclusion_mode(start)
        response = sync_async_client.send_sync_msg(msg,"/ta/zw/commands","/ta/zw/events",timeout=30,correlation_type="MSG_TYPE",correlation_msg_type="zw_ta.inclusion_report")
        log.info("Inclusion mode operation is completed")
        jobj = json.dumps(response)
    elif action == "zw_exclusion_mode":
        log.info("Setting zwave controller into exclusion mode")
        start =  libs.utils.convert_bool(request.form["start"])
        msg = zwapi.exclusion_mode(start)
        response = sync_async_client.send_sync_msg(msg,"/ta/zw/commands","/ta/zw/events",timeout=30,correlation_type="MSG_TYPE",correlation_msg_type="zw_ta.exclusion_report")
        log.info("Exclusion mode operation is completed")
        jobj = json.dumps(response)

    elif action == "remove_failed_node":
        node_id = int(request.form["node_id"])
        msg = zwapi.remove_failed_node(node_id)
        mqtt.publish("/ta/zw/commands",json.dumps(msg),1)
        jobj = json.dumps({})

    elif action == "replace_failed_node":
        node_id = int(request.form["node_id"])
        msg = zwapi.replace_failed_node(node_id)
        mqtt.publish("/ta/zw/commands",json.dumps(msg),1)
        jobj = json.dumps({})

    elif action == "ping_node":
        node_id = int(request.form["node_id"])
        msg = zwapi.net_ping(node_id)
        # mqtt.publish("/ta/zw/commands",json.dumps(msg),1)
        response = sync_async_client.send_sync_msg(msg,"/ta/zw/commands","/ta/zw/events",timeout=30,correlation_type="MSG_TYPE",correlation_msg_type="net.ping_report")
        jobj = json.dumps(response)

    elif action == "get_node_info":
        log.info("Requesting node info")
        node_id = int(request.form["node_id"])
        msg = zwapi.get_node_info(node_id)
        response = sync_async_client.send_sync_msg(msg,"/ta/zw/commands","/ta/zw/events",timeout=30,correlation_type="MSG_TYPE",correlation_msg_type="zw_ta.inclusion_report")
        log.info("Inclusion mode operation is completed")
        jobj = json.dumps(response)

    elif action == "get_network_graph":
        # getting network infor from cache
        response = cache.get("zw_ta.routing_info","/ta/zw/events")
        routing_info = response["raw_msg"]["event"]["properties"]
        graph = ZwaveTools().get_network_graph(routing_info)
        jobj = json.dumps(graph)

    else :
        jobj = json.dumps({})
    return Response(response=jobj, mimetype='application/json')


@app.route('/ui/msg_history',methods=["GET","POST"])
@login_required
def msg_history():
    log.info("Msg history")

    dev_id = request.args.get("dev_id",None)
    # 0
    start = int(request.args.get("start",0))
    # 2504836694
    end = int(request.args.get("stop",3504836694))

    history = timeseries.get_msg_history(dev_id,start,end)
    # history = json.dumps(ts)
    return render_template('msg_history.html',history=history,global_context=global_context)

@app.route('/ui/tools',methods=["POST","GET"])
@login_required
def tools():
    tools = Tools()
    output = ""
    services = []
    logs = []
    try:
        if request.method == "POST":
            action = request.form["action"]
            log.info("Tools request.action="+action)
            if action == "start_service":
                service_name = request.form["service_name"]
                output = tools.start_service(service_name)
            elif action == "stop_service":
                service_name = request.form["service_name"]
                output = tools.stop_service(service_name)
            elif action == "query_status":
                service_name = request.form["service_name"]
                output = tools.process_status(service_name)
            elif action == "kill_process":
                service_name = request.form["service_name"]
                output = tools.kill_process(service_name)
        logs = tools.get_logfiles()
        services = tools.get_services()
    except Exception as ex :
        output = str(ex)

    return render_template('tools.html',output=output ,global_context=global_context,logs=logs,services=services,autoescape=False)

@app.route('/ui/updates',methods=["POST","GET"])
@login_required
def updates():
    import urllib2
    import os

    distro_uri = msg_man.global_configs["system"]["distro_server_uri"]
    build_info_path = os.path.join(os.getcwd(), "configs", "build_info.json")
    current_info = json.load(file(build_info_path))
    develop_info = json.load(urllib2.urlopen(distro_uri+"/develop/build_info.json",timeout=15))
    master_info = json.load(urllib2.urlopen(distro_uri+"/build_info.json",timeout=15))
    log.debug(develop_info)
    log.debug(master_info)
    status = ""
    if request.method == "POST":
        tools = Tools()
        action = request.form["action"]
        if action == "update_to_master":
            tools.run_update_procedure(distro_uri)
        if action == "update_to_develop":
            tools.run_update_procedure(distro_uri+"/develop")
        status = "Update procedure is in progres..... please check /var/log/blackfly_upgrade.log for details "

    return render_template('updates.html',global_context=global_context,current_info=current_info,develop_info=develop_info,master_info=master_info,autoescape=False,status=status)

@app.route('/ui/logviewer',methods=["POST","GET"])
@login_required
def log_viewer():
    tools = Tools()
    log_file = request.form["log_file"]
    tail_size = request.form["tail_size"]
    search = request.form["search"]

    output = tools.tail_log(log_file,int(tail_size),search)
    output = "<pre>"+output+"</pre>"
    return output

@app.route('/ui/mqtt_client',methods=["POST","GET"])
@login_required
def mqtt_client():
    status = ""
    if request.method == "POST":
        address = request.form["address"]
        payload = request.form["payload"]
        log.info(type(payload))
        log.info("Payload"+str(payload))
        mqtt.publish(address,str(payload),1)
        status = "The message was sent"

    return render_template('mqtt_client.html',global_context=global_context,status=status)

@app.route('/ui/work_session',methods=["POST","GET"])
@login_required
def work_session():
    status = ""

    if request.method == "POST":
        # 1) Reset address mapping
        # 2) Reset timeseries DB
        # 3) Update topic prefix in settings
        # 4) Reconnect to broker
        gateway_id = request.form["gateway_id"]
        new_gateway_id = gateway_id
        start_fresh = False
        if "start_fresh" in request.form:
            start_fresh = True
        msg_man.global_configs["mqtt"]["global_topic_prefix"] = gateway_id
        msg_man.serialize_global_config()
        mqtt.set_mqtt_params(msg_man.global_configs["mqtt"]["client_id"],msg_man.global_configs["mqtt"]["username"],msg_man.global_configs["mqtt"]["password"],msg_man.global_configs["mqtt"]["global_topic_prefix"],msg_man.global_configs["mqtt"]["enable_sys"])
        mqtt.stop()
        mqtt.start()
        if start_fresh:
            msg_man.reset_address_mapping()
            timeseries.delete_all_for_dev("all")
            timeseries.delete_msg_history("all")

    elif request.method == "GET":
       new_gateway_id = request.args.get("new_gateway_id",msg_man.global_configs["mqtt"]["global_topic_prefix"] )

    gateway_id = msg_man.global_configs["mqtt"]["global_topic_prefix"]
    return render_template('work_session.html',global_context=global_context,gateway_id = gateway_id,new_gateway_id=new_gateway_id)



if __name__ == '__main__':
    # import cProfile
    # cProfile.run('app.run(host="0.0.0.0",port = http_server_port,debug=True, use_debugger=False,threaded=True,use_reloader=False)')
    app.run(host="0.0.0.0",port = http_server_port,debug=True, use_debugger=True,threaded=True,use_reloader=False)
