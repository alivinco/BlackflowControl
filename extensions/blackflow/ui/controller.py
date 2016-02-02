from extensions.blackflow.app_graph_manager import AppGraphManager
from libs.utils import split_app_full_name

__author__ = 'alivinco'
import json
import logging
from flask import render_template, Blueprint, request, Response
from libs.flask_login import LoginManager, login_required
from flask import Response, redirect
from libs.dmapi import blackflow
from libs import utils

log = logging.getLogger("bf_blackflow")

# the variables should be set by main app
global_context = None
sync_async_client = None

blackflowapi = blackflow.Blackflow("app", "blackfly", "blackfly")

blackflow_bp = Blueprint('blackflow_bp', __name__)
login_manager = LoginManager()
login_manager.login_view = "/ui/login"


@blackflow_bp.route('/ui/blackflow/<inst_name>/context', methods=["GET"])
@login_required
def app_context(inst_name):
    log.info("Blackflow context get")
    msg = blackflowapi.context_get()
    response = sync_async_client.send_sync_msg(msg, "/app/blackflow/%s/commands"%inst_name, "/app/blackflow/%s/events"%inst_name, timeout=10,correlation_msg_type="blackflow.context",correlation_type="MSG_TYPE")
    return render_template('blackflow/context.html', bf_response=response,bf_inst_name = inst_name, global_context=global_context,format_time = utils.format_iso_time_from_sec)


@blackflow_bp.route('/ui/blackflow/<inst_name>/apps', methods=["GET"])
@login_required
def apps(inst_name):
    log.info("Blackflow Apps")
    msg = blackflowapi.get_apps()
    response = sync_async_client.send_sync_msg(msg, "/app/blackflow/%s/commands"%inst_name, "/app/blackflow/%s/events"%inst_name, timeout=10,correlation_msg_type="blackflow.apps",correlation_type="MSG_TYPE")
    return render_template('blackflow/apps.html', bf_response=response,bf_inst_name = inst_name ,global_context=global_context,format_time = utils.format_iso_time_from_sec)


@blackflow_bp.route('/ui/blackflow/<bf_inst_name>/app_instances', methods=["GET"])
@login_required
def app_instances(bf_inst_name):
    log.info("Blackflow Apps")
    msg = blackflowapi.get_app_instances()
    response = sync_async_client.send_sync_msg(msg, "/app/blackflow/%s/commands"%bf_inst_name, "/app/blackflow/%s/events"%bf_inst_name, timeout=10,correlation_msg_type="blackflow.app_instances",correlation_type="MSG_TYPE")
    app_instance_state = {
        0:"STOPPED",
        1:"LOADED",
        2:"INITIALIZED",
        3:"RUNNING",
        4:"PAUSED",
        5:"STOPPED_WITH_ERROR",
        6:"PAUSED_WITH_ERROR"
    }

    def mod_response(item):
        item["state"] = app_instance_state[item["state"]]
        return item
    response["event"]["properties"]["app_instances"] = map(mod_response,response["event"]["properties"]["app_instances"])

    return render_template('blackflow/app_instances.html', bf_response=response,bf_inst_name = bf_inst_name, global_context=global_context,format_time = utils.format_iso_time_from_sec)


@blackflow_bp.route('/ui/blackflow/<inst_name>/app_instance_config', methods=["GET"])
@login_required
def app_instance_config(inst_name):
    log.info("Blackflow App instance configurator")
    inst_id = int(request.args.get("id",0))
    app_name = request.args.get("app_name","")
    return render_template('blackflow/app_instance_config.html',bf_inst_name=inst_name, inst_id=inst_id,app_name = app_name ,global_context=global_context,format_time = utils.format_iso_time_from_sec)


@blackflow_bp.route('/api/blackflow/<inst_name>/proxy', methods=["POST"])
@login_required
def blackflow_proxy(inst_name):
    """
    The method is a proxy between javascript client and MQTT.
    Proxy support 2 types of request : one_way and sync_response
    corr_type should be - "MSG_TYPE","COR_ID" . Where MSG_TYPE - message correlated by message type , COR_ID - correlated by cor_id property.

    """
    # supported types : one_way , sync_response
    request_topic = "/app/blackflow/%s/commands"%inst_name
    response_topic = "/app/blackflow/%s/events"%inst_name
    data = request.get_json()
    request_type = data["req_type"] if "req_type" in data else "one_way"
    correlation_msg_type = data["corr_msg_type"] if "corr_msg_type" in data else ""
    correlation_type = data["corr_type"] if "corr_type" in data else "MSG_TYPE"
    sync_request_timeout = int(data["sync_req_timeout"]) if "sync_req_timeout" in data else 30
    request_payload = json.dumps(data["req_payload"])
    log.info("Proxy request . type = %s , correlation_msg_type = %s , request_payload = %s "%(request_type,correlation_msg_type,request_payload))
    if request_type == "one_way":
        sync_async_client.msg_system.publish(request_topic,request_payload,1)
        response = "{}"
    elif request_type == "sync_response":
        request_payload = data["req_payload"]
        response = sync_async_client.send_sync_msg(request_payload, request_topic,response_topic, sync_request_timeout,correlation_msg_type=correlation_msg_type,correlation_type=correlation_type)
        response = json.dumps(response)
    return Response(response=response, mimetype='application/json' )


@blackflow_bp.route('/ui/blackflow/<inst_name>/app_instances_graph', methods=["GET"])
@login_required
def app_instances_graph_ui(inst_name):
    return render_template('blackflow/app_instances_graph.html', bf_inst_name=inst_name, global_context=global_context,format_time = utils.format_iso_time_from_sec)


@blackflow_bp.route('/ui/blackflow/<inst_name>/app_editor', methods=["GET"])
@login_required
def app_editor_ui(inst_name):
    app_name = request.args.get("app_name","")
    return render_template('blackflow/app_editor.html',app_name= app_name,bf_inst_name=inst_name, global_context=global_context,format_time = utils.format_iso_time_from_sec)


@blackflow_bp.route('/ui/blackflow/<inst_name>/app_store', methods=["GET"])
@login_required
def app_store_ui(inst_name):
    return render_template('blackflow/app_store.html',bf_inst_name=inst_name, global_context=global_context, format_time=utils.format_iso_time_from_sec)

@blackflow_bp.route('/ui/blackflow/<inst_name>/containers', methods=["GET"])
@login_required
def containers_ui(inst_name):
    return render_template('blackflow/containers.html',bf_inst_name=inst_name, global_context=global_context, format_time=utils.format_iso_time_from_sec)


@blackflow_bp.route('/api/blackflow/<inst_name>/containers', methods=["GET"])
@login_required
def containers_api(inst_name):
    response = sync_async_client.send_sync_msg(msg, "/app/blackflow/%s/commands"%inst_name, "/app/blackflow/%s/events"%inst_name, timeout=5,correlation_msg_type="blackflow.apps",correlation_type="MSG_TYPE")

@blackflow_bp.route('/api/blackflow/<inst_name>/app_instance_config', methods=["GET"])
@login_required
def app_instance_config_api(inst_name):
    log.info("Blackflow App instance configurator")
    inst_id = int(request.args.get("id",0))
    app_full_name = request.args.get("app_name","")
    developer, app_name, version = split_app_full_name(app_full_name)
    # app_name =
    msg = blackflowapi.get_apps()
    # getting list of application manifests
    response = sync_async_client.send_sync_msg(msg, "/app/blackflow/%s/commands"%inst_name, "/app/blackflow/%s/events"%inst_name, timeout=5,correlation_msg_type="blackflow.apps",correlation_type="MSG_TYPE")
    app_manifest = filter(lambda app:app["developer"]==developer and app["name"]==app_name and app["version"]==version,response["event"]["properties"]["apps"])[0]
    # getting a list of instance configurations
    msg = blackflowapi.get_app_instances()
    all_app_instances = sync_async_client.send_sync_msg(msg, "/app/blackflow/%s/commands"%inst_name, "/app/blackflow/%s/events"%inst_name, timeout=5,correlation_msg_type="blackflow.app_instances",correlation_type="MSG_TYPE")
    if inst_id :
        app_instance = filter(lambda inst:inst["id"]==inst_id,all_app_instances["event"]["properties"]["app_instances"])[0]
        for key,sub in app_instance["sub_for"].iteritems():
            if key in app_manifest["sub_for"] :sub["app_def"] = app_manifest["sub_for"][key]
        for key,pub in  app_instance["pub_to"].iteritems():
            if key in app_manifest["pub_to"] : pub["app_def"] = app_manifest["pub_to"][key]
    else:
        app_instance = {"id":None,"app_full_name":app_full_name,"alias":"","sub_for":{},"pub_to":{},"configs":{},"comments":""}
        for key , sub in app_manifest["sub_for"].iteritems():
            topic = sub["topic"] if "topic" in sub else ""
            app_instance["sub_for"][key] = {"topic":topic,"app_def":sub}
        for key , pub in app_manifest["pub_to"].iteritems():
            app_instance["pub_to"][key] = {"topic":"","app_def":pub}
        for conf in app_manifest["configs"]:
            app_instance["configs"][conf] = ""

    result_json = json.dumps(app_instance)
    return Response(response=result_json, mimetype='application/json' )


@blackflow_bp.route('/api/blackflow/<inst_name>/app_instances_graph', methods=["GET"])
@login_required
def app_instances_graph(inst_name):
    log.info("Blackflow Apps")
    msg = blackflowapi.get_app_instances()
    response = sync_async_client.send_sync_msg(msg, "/app/blackflow/%s/commands"%inst_name, "/app/blackflow/%s/events"%inst_name, timeout=5,correlation_msg_type="blackflow.app_instances",correlation_type="MSG_TYPE")
    graph = AppGraphManager(response["event"]["properties"]["app_instances"]).convert_app_instances_into_graph()
    graph_json = json.dumps(graph)
    return Response(response=graph_json, mimetype='application/json' )


@blackflow_bp.route('/api/blackflow/<inst_name>/analytics', methods=["GET"])
@login_required
def blackflow_analytics(inst_name):
    log.info("Blackflow analytics")
    msg = blackflowapi.get_analytics()
    response = sync_async_client.send_sync_msg(msg, "/app/blackflow/%s/commands"%inst_name, "/app/blackflow/%s/events"%inst_name, timeout=5,correlation_msg_type="blackflow.analytics",correlation_type="MSG_TYPE")
    result = json.dumps(response["event"]["properties"])
    return Response(response=result, mimetype='application/json' )