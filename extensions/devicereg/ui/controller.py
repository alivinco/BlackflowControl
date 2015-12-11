import json

__author__ = 'alivinco'
import logging
from flask import render_template, Blueprint, request, Response, url_for
from libs.flask_login import LoginManager, login_required
from libs.dmapi import devicereg
from flask import Response, redirect
from libs.dmapi import config
from libs.dmapi import association

log = logging.getLogger("bf_web")

# the variables should be set by main app
global_context = {}
sync_async_client = None
msg_man = None
devreg_bp = Blueprint('devicereg_bp', __name__)
login_manager = LoginManager()
login_manager.login_view = "/ui/login"
deviceregapi = devicereg.Devicereg("app", "blackfly", "blackfly")


@devreg_bp.route('/ui/dr_browser', methods=["GET"])
@login_required
def dr_browser():
    log.info("Device registry browser")
    device_id = request.args.get("Id", "")
    if device_id:
        msg = deviceregapi.get_device_by_id(int(device_id))
    else:
        msg = deviceregapi.get_device_list()

    response = sync_async_client.send_sync_msg(msg, "/app/devicereg/commands", "/app/devicereg/events", timeout=5)
    log.debug("response :" + str(response))

    return render_template('devicereg/dr_device_browser.html', dr_response=response, global_context=global_context,
                           configs=msg_man.global_configs)


@devreg_bp.route('/api/dr_browser', methods=["POST"])
@login_required
def dr_browser_api():
    if request.method == "POST":
        action = request.form["action"]
        device_id = int(request.form["device_id"])
        if action == "field_update":
            field_name = request.form["field_name"]
            field_value = request.form["field_value"]
            msg = deviceregapi.update({"Id": device_id}, {field_name: field_value})
            log.info(msg)
            sync_async_client.send_sync_msg(msg, "/app/devicereg/commands", "/app/devicereg/events", timeout=2)
            return redirect(url_for(".dr_browser"))

        elif action == "config_set" or action == "config_get":
            config_type = request.form["config_type"]
            config_name = request.form["config_name"]
            config_value = request.form["config_value"]
            topic = request.form["config_topic"]
            if "/zw/" in topic and config_name :
                    config_name = int(config_name)
            if "/zw/" in topic and config_value :
                    config_value = int(config_value)

            if config_type == "config":
                confapi = config.Config("app", "blackfly", "blackfly")
                msg = None
                if action == "config_set" and config_value and config_name:
                    msg = confapi.set(config_name, config_value)
                elif action == "config_get" and config_name:
                    msg = confapi.get(config_name)
                else :
                    log.info("One of manadatory parameters is empty")

            elif config_type == "assoc":
                confapi = association.Association("app", "blackfly", "blackfly")
                msg = None
                if action == "config_set" and config_value and config_name:
                    msg = confapi.set(config_name, config_value)
                elif action == "config_get" and config_name:
                    msg = confapi.get(config_name)
                else :
                    log.info("One of manadatory parameters is empty")

            if msg:
                sync_async_client.msg_system.publish(topic, json.dumps(msg), 1)

            log.info("Configuration command of type = %s , name = %s , value = %s value was sent" % (
                config_type, config_name, config_value))
            return redirect(url_for(".dr_browser"))

        elif action == "delete":
            msg = deviceregapi.delete(device_id)
            sync_async_client.send_sync_msg(msg, "/app/devicereg/commands", "/app/devicereg/events", timeout=2)
        elif action == "init_device":
            device_id = int(device_id)
            msg = deviceregapi.get_device_by_id(device_id)
            device = sync_async_client.send_sync_msg(msg, "/app/devicereg/commands", "/app/devicereg/events",timeout=10)
            if len(device["event"]["properties"]["device_list"]["value"])>1:
                log.warn("Old device registry . You need to upgrade to newer version.")
            device = filter(lambda dev:dev["Id"] == device_id ,device["event"]["properties"]["device_list"]["value"])
            if len(device) > 0:
                services = device[0]["EndPoint"]
                device_alias = device[0]["Alias"]
                msg_man.generate_address_mappings_for_services(services, device_alias)
                response_status = {"status": "ok"}
            else:
                log.warn("Empty response from device registry")
                response_status = {"status": "error", "description": "Empty response from device registry"}

        return Response(response=json.dumps(response_status), mimetype='application/json')
