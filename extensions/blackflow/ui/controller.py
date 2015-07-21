from extensions.blackflow.app_graph_manager import AppGraphManager

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


@blackflow_bp.route('/ui/blackflow/context', methods=["GET"])
@login_required
def blackflow_app_context():
    log.info("Blackflow context get")
    msg = blackflowapi.context_get()
    response = sync_async_client.send_sync_msg(msg, "/app/blackflow/commands", "/app/blackflow/events", timeout=5,correlation_msg_type="blackflow.context",correlation_type="MSG_TYPE")
    return render_template('blackflow/context.html', bf_response=response, global_context=global_context,format_time = utils.format_iso_time_from_sec)

@blackflow_bp.route('/ui/blackflow/apps', methods=["GET"])
@login_required
def blackflow_apps():
    log.info("Blackflow Apps")
    msg = blackflowapi.get_apps()
    response = sync_async_client.send_sync_msg(msg, "/app/blackflow/commands", "/app/blackflow/events", timeout=5,correlation_msg_type="blackflow.apps",correlation_type="MSG_TYPE")
    return render_template('blackflow/apps.html', bf_response=response, global_context=global_context,format_time = utils.format_iso_time_from_sec)

@blackflow_bp.route('/ui/blackflow/app_instances', methods=["GET"])
@login_required
def blackflow_app_instances():
    log.info("Blackflow Apps")
    msg = blackflowapi.get_app_instances()
    response = sync_async_client.send_sync_msg(msg, "/app/blackflow/commands", "/app/blackflow/events", timeout=5,correlation_msg_type="blackflow.app_instances",correlation_type="MSG_TYPE")
    return render_template('blackflow/app_instances.html', bf_response=response, global_context=global_context,format_time = utils.format_iso_time_from_sec)

@blackflow_bp.route('/ui/blackflow/app_instance_config/<inst_id>', methods=["GET"])
@login_required
def blackflow_app_instance_config(inst_id):
    log.info("Blackflow App instance configurator")
    msg = blackflowapi.get_app_instances()
    response = sync_async_client.send_sync_msg(msg, "/app/blackflow/commands", "/app/blackflow/events", timeout=5,correlation_msg_type="blackflow.app_instances",correlation_type="MSG_TYPE")
    return render_template('blackflow/app_instance_config.html', bf_response=response, global_context=global_context,format_time = utils.format_iso_time_from_sec)


@blackflow_bp.route('/ui/blackflow/app_instances_graph', methods=["GET"])
@login_required
def blackflow_app_instances_graph_ui():
    return render_template('blackflow/app_instances_graph.html', global_context=global_context,format_time = utils.format_iso_time_from_sec)

@blackflow_bp.route('/api/blackflow/app_instances_graph', methods=["GET"])
@login_required
def blackflow_app_instances_graph():
    log.info("Blackflow Apps")
    msg = blackflowapi.get_app_instances()
    response = sync_async_client.send_sync_msg(msg, "/app/blackflow/commands", "/app/blackflow/events", timeout=5,correlation_msg_type="blackflow.app_instances",correlation_type="MSG_TYPE")
    graph = AppGraphManager(response["event"]["properties"]["app_instances"]).convert_app_instances_into_graph()
    graph_json = json.dumps(graph)
    return Response(response=graph_json, mimetype='application/json' )

@blackflow_bp.route('/api/blackflow/analytics', methods=["GET"])
@login_required
def blackflow_analytics():
    log.info("Blackflow analytics")
    msg = blackflowapi.get_analytics()
    response = sync_async_client.send_sync_msg(msg, "/app/blackflow/commands", "/app/blackflow/events", timeout=5,correlation_msg_type="blackflow.analytics",correlation_type="MSG_TYPE")
    result = json.dumps(response["event"]["properties"])
    return Response(response=result, mimetype='application/json' )