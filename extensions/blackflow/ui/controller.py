from extensions.blackflow.app_graph_manager import AppGraphManager
from libs.iot_msg_lib.iot_msg import MsgType, IotMsg
from libs.iot_msg_lib.iot_msg_converter import IotMsgConverter
from libs.utils import split_app_full_name
import json
import logging
from flask import render_template, Blueprint, request, Response
from libs.flask_login import LoginManager, login_required,current_user
from flask import Response, redirect
from libs import utils
from modules.mod_containers import ServiceDiscovery

__author__ = 'alivinco'

log = logging.getLogger("bf_blackflow")

# the variables should be set by main app
global_context = None
sync_async_client = None

blackflow_bp = Blueprint('blackflow_bp', __name__)
login_manager = LoginManager()
app_name = "bfctrl"
svc_discovery = None


@blackflow_bp.route('/ui/context', methods=["GET"])
@login_required
def app_context():
    log.info("Blackflow context get")
    result = dict()
    msg = IotMsg("blackflow", MsgType.CMD, "blackflow", "context_get")
    for container_id in svc_discovery.get_containers():
        response = sync_async_client.send_sync_msg(msg, "jim1/cmd/app/blackflow/%s" % container_id, "jim1/evt/app/blackflow/%s" % container_id, timeout=10,
                                                   correlation_msg_type="blackflow.context", correlation_type="MSG_TYPE")
        if response:
            result[container_id] = response.get_properties()

    return render_template('blackflow/context.html', bf_response=result, global_context=global_context,
                           format_time=utils.format_iso_time_from_sec)


@blackflow_bp.route('/ui/apps', methods=["GET"])
@login_required
def apps():
    log.info("Blackflow Apps")
    result = list()
    msg = IotMsg("blackflow", MsgType.CMD, "blackflow", "get_apps")
    containers = svc_discovery.get_containers()
    for container_id in containers:
        response = sync_async_client.send_sync_msg(msg, "jim1/cmd/app/blackflow/%s" % container_id, "jim1/evt/app/blackflow/%s" % container_id, timeout=10,
                                                   correlation_msg_type="blackflow.apps", correlation_type="MSG_TYPE")
        if response :
            props = response.get_properties()
            for item in props["apps"] :
                item["container_id"] = container_id
        result.extend(props["apps"])

    return render_template('blackflow/apps.html', bf_response=result, containers = containers, global_context=global_context, format_time=utils.format_iso_time_from_sec)


@blackflow_bp.route('/ui/app_instances', methods=["GET"])
@login_required
def app_instances():
    log.info("Blackflow Apps")
    msg = IotMsg("blackflow", MsgType.CMD, "blackflow", "get_app_instances")
    result = list()
    for container_id in svc_discovery.get_containers():
        response = sync_async_client.send_sync_msg(msg, "jim1/cmd/app/blackflow/%s" % container_id, "jim1/evt/app/blackflow/%s" % container_id, timeout=10,
                                                   correlation_msg_type="blackflow.app_instances", correlation_type="MSG_TYPE")
        app_instance_state = {
            0: "STOPPED",
            1: "LOADED",
            2: "INITIALIZED",
            3: "RUNNING",
            4: "PAUSED",
            5: "STOPPED_WITH_ERROR",
            6: "PAUSED_WITH_ERROR"
        }

        def mod_response(item):
            item["state"] = app_instance_state[item["state"]]
            item["container_id"] = container_id
            return item
        if response:
            response.get_properties()["app_instances"] = map(mod_response, response.get_properties()["app_instances"])
            result.extend(response.get_properties()["app_instances"])

    return render_template('blackflow/app_instances.html', bf_response=result, global_context=global_context,
                           format_time=utils.format_iso_time_from_sec)


@blackflow_bp.route('/ui/app_instance_config', methods=["GET"])
@login_required
def app_instance_config():
    log.info("Blackflow App instance configurator")
    inst_id = int(request.args.get("id", 0))
    container_id = request.args.get("container_id", 0)
    app_name = request.args.get("app_name", "")
    return render_template('blackflow/app_instance_config.html', bf_inst_name=container_id, inst_id=inst_id, app_name=app_name, global_context=global_context,
                           format_time=utils.format_iso_time_from_sec)


@blackflow_bp.route('/api/proxy', methods=["POST"])
@login_required
def blackflow_proxy():
    """
    The method is a proxy between javascript client and MQTT.
    Proxy support 2 types of request : one_way and sync_response
    corr_type should be - "MSG_TYPE","COR_ID" . Where MSG_TYPE - message correlated by message type , COR_ID - correlated by cor_id property.

    """
    data = request.get_json()
    inst_name = data["container_id"]
    # supported types : one_way , sync_response
    request_topic = "/cmd/app/blackflow/%s" % inst_name
    response_topic = "/evt/app/blackflow/%s" % inst_name
    request_type = data["req_type"] if "req_type" in data else "one_way"
    correlation_msg_type = data["corr_msg_type"] if "corr_msg_type" in data else ""
    correlation_type = data["corr_type"] if "corr_type" in data else "MSG_TYPE"
    sync_request_timeout = int(data["sync_req_timeout"]) if "sync_req_timeout" in data else 30
    request_payload = data["req_payload"]
    log.info("Proxy request . type = %s , correlation_msg_type = %s , request_payload = %s " % (request_type, correlation_msg_type, request_payload))
    if request_type == "one_way":
        msg = IotMsgConverter.dict_to_iot_msg(request_topic,request_payload)
        sync_async_client.msg_system.publish("jim1"+request_topic, msg, 1)
        return Response(response="{}" , mimetype='application/json')
    elif request_type == "sync_response":
        request_payload = data["req_payload"]
        msg = IotMsgConverter.dict_to_iot_msg(request_topic,request_payload)
        response = sync_async_client.send_sync_msg(msg, "jim1"+request_topic, "jim1"+response_topic, sync_request_timeout, correlation_msg_type=correlation_msg_type,
                                                   correlation_type=correlation_type)
        return Response(response=IotMsgConverter.iot_msg_with_topic_to_str(response_topic,response) , mimetype='application/json')


@blackflow_bp.route('/ui/app_instances_graph/', methods=["GET"])
@login_required
def app_instances_graph_ui():
    return render_template('blackflow/app_instances_graph.html', global_context=global_context, format_time=utils.format_iso_time_from_sec)


@blackflow_bp.route('/ui/app_editor', methods=["GET"])
@login_required
def app_editor_ui():
    inst_name = request.args.get("container_id", "")
    app_name = request.args.get("app_name", "")
    return render_template('blackflow/app_editor.html', app_name=app_name, bf_inst_name=inst_name, global_context=global_context,
                           format_time=utils.format_iso_time_from_sec)


@blackflow_bp.route('/ui/app_store', methods=["GET"])
@login_required
def app_store_ui():
    containers = svc_discovery.get_containers()
    log.debug(current_user.username)
    return render_template('blackflow/app_store.html', containers=containers, global_context=global_context, format_time=utils.format_iso_time_from_sec ,current_user = current_user )


@blackflow_bp.route('/ui/discovery', methods=["GET"])
@login_required
def discovery_ui():
    rediscover = True if request.args.get("rediscover", None) else False
    result = svc_discovery.discover(force_rediscover = rediscover)
    return render_template('blackflow/containers.html', global_context=global_context, format_time=utils.format_iso_time_from_sec,containers = result )


@blackflow_bp.route('/api/containers', methods=["GET"])
@login_required
def containers_api():
    pass

@blackflow_bp.route('/api/app_instance_config', methods=["GET"])
@login_required
def app_instance_config_api():
    log.info("Blackflow App instance configurator")
    inst_id = int(request.args.get("id", 0))
    inst_name = request.args.get("container_id", "")
    app_full_name = request.args.get("app_name", "")
    developer, app_name, version = split_app_full_name(app_full_name)
    msg = IotMsg("blackflow", MsgType.CMD, "blackflow", "get_apps")
    msg.set_properties({"filter":{"name":app_name,"version":version , "developer":developer}})
    # getting application manifest
    response = sync_async_client.send_sync_msg(msg, "jim1/cmd/app/blackflow/%s" % inst_name, "jim1/evt/app/blackflow/%s" % inst_name, timeout=5,
                                               correlation_msg_type="blackflow.apps", correlation_type="MSG_TYPE")
    # app_manifest = filter(lambda app: app["developer"] == developer and app["name"] == app_name and app["version"] == version, response.get_properties()["apps"])[0]
    if response:
        app_manifest = response.get_properties()["apps"][0]
    else :
        log.error("Can't get application manifest from container.")
        return Response(response=json.dumps([]), mimetype='application/json')

    # getting application instance config
    msg = IotMsg("blackflow", MsgType.CMD, "blackflow", "get_app_instances")
    msg.set_properties({"filter": {"id": inst_id}})
    all_app_instances = sync_async_client.send_sync_msg(msg, "jim1/cmd/app/blackflow/%s" % inst_name, "jim1/evt/app/blackflow/%s" % inst_name, timeout=5,
                                                        correlation_msg_type="blackflow.app_instances", correlation_type="MSG_TYPE")
    if all_app_instances:
        if inst_id :
            # Existing app instance
            # app_instance = filter(lambda inst: inst["id"] == inst_id, all_app_instances.get_properties()["app_instances"])[0]
            app_instance = all_app_instances.get_properties()["app_instances"][0]
            for key, sub in app_instance["sub_for"].iteritems():
                if key in app_manifest["sub_for"]: sub["app_def"] = app_manifest["sub_for"][key]
            for key, pub in app_instance["pub_to"].iteritems():
                if key in app_manifest["pub_to"]: pub["app_def"] = app_manifest["pub_to"][key]
        else:
            # New app instance
            app_instance = {"id": None, "app_full_name": app_full_name, "alias": "", "sub_for": {}, "pub_to": {}, "configs": {}, "comments": ""}
            for key, sub in app_manifest["sub_for"].iteritems():
                topic = sub["topic"] if "topic" in sub else ""
                msg_type = sub["msg_type"] if "msg_type" in sub else ""
                app_instance["sub_for"][key] = {"topic": topic, "app_def": sub, "msg_type":msg_type}
            for key, pub in app_manifest["pub_to"].iteritems():
                topic = pub["topic"] if "topic" in pub else ""
                msg_type = pub["msg_type"] if "msg_type" in pub else ""
                app_instance["pub_to"][key] = {"topic": topic, "app_def": pub,"msg_type":msg_type}
            for conf in app_manifest["configs"]:
                app_instance["configs"][conf] = ""
    else :
        log.error("Can't get app instance from container . Reason : Empty response")
        app_instance = []

    result_json = json.dumps(app_instance)
    return Response(response=result_json, mimetype='application/json')


@blackflow_bp.route('/api/app_instances_graph', methods=["GET"])
@login_required
def app_instances_graph():
    log.info("Blackflow Instances graph")
    result = {"nodes":[],"edges":[]}
    for container_id in svc_discovery.get_containers():

        msg = IotMsg("blackflow", MsgType.CMD, "blackflow", "get_app_instances")
        response = sync_async_client.send_sync_msg(msg, "jim1/cmd/app/blackflow/%s" % container_id, "jim1/evt/app/blackflow/%s" % container_id, timeout=5,
                                                   correlation_msg_type="blackflow.app_instances", correlation_type="MSG_TYPE")
        graph = AppGraphManager(response.get_properties()["app_instances"],container_id).convert_app_instances_into_graph()
        result["nodes"].extend(graph["nodes"])
        result["edges"].extend(graph["edges"])
    return Response(response=json.dumps(result), mimetype='application/json')


@blackflow_bp.route('/api/analytics', methods=["GET"])
@login_required
def blackflow_analytics():
    log.info("Blackflow analytics")
    result = []
    for container_id in svc_discovery.get_containers():
        msg = IotMsg("blackflow", MsgType.CMD, "blackflow", "analytics_get")
        response = sync_async_client.send_sync_msg(msg, "jim1/cmd/app/blackflow/%s" % container_id, "jim1/evt/app/blackflow/%s" % container_id, timeout=5,
                                                   correlation_msg_type="blackflow.analytics", correlation_type="MSG_TYPE")
        if response:
            result.extend(response.get_properties()["link_counters"])
    return Response(response=json.dumps(result), mimetype='application/json')
