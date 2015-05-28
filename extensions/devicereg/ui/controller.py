import json

__author__ = 'alivinco'
import logging
from libs.sync_to_async_msg_converter import SyncToAsyncMsgConverter
from flask import render_template, Blueprint, request, Response
from libs.flask_login import LoginManager,  login_required
from libs.dmapi import devicereg

log = logging.getLogger("bf_web")
# the variables should be set by main app
global_context = None
sync_async_client = None
msg_man = None

devreg_bp = Blueprint('devicereg_bp', __name__)
login_manager = LoginManager()
login_manager.login_view = "/ui/login"
deviceregapi = devicereg.Devicereg("app","blackfly","blackfly")


@devreg_bp.route('/ui/dr_browser',methods=["GET"])
@login_required
def dr_browser():
    log.info("Device registry browser")
    device_id = request.args.get("Id","")
    if device_id:
        msg = deviceregapi.get_device_by_id(int(device_id))
    else :
        msg = deviceregapi.get_device_list()

    response = sync_async_client.send_sync_msg(msg,"/app/devicereg/commands","/app/devicereg/events",timeout=5)
    log.debug("response :"+str(response))

    return render_template('devicereg/dr_device_browser.html',dr_response=response,global_context=global_context,configs = msg_man.global_configs)

@devreg_bp.route('/api/dr_browser',methods=["POST"])
@login_required
def dr_browser_api():
    if request.method == "POST":
        action = request.form["action"]
        device_id = int(request.form["device_id"])
        if action == "update":
            field_name = request.form["field_name"]
            field_value = request.form["field_value"]
            msg = deviceregapi.update({"Id":device_id},{field_name:field_value})
            log.info(msg)
            sync_async_client.send_sync_msg(msg,"/app/devicereg/commands","/app/devicereg/events",timeout=2)
        elif action == "delete":
            msg = deviceregapi.delete(device_id)
            sync_async_client.send_sync_msg(msg,"/app/devicereg/commands","/app/devicereg/events",timeout=2)
        elif action == "init_device":
            msg = deviceregapi.get_device_by_id(int(device_id))
            device = sync_async_client.send_sync_msg(msg,"/app/devicereg/commands","/app/devicereg/events",timeout=10)
            services = device["event"]["properties"]["device_list"]["value"][0]["EndPoint"]
            device_alias = device["event"]["properties"]["device_list"]["value"][0]["Alias"]
            msg_man.generate_address_mappings_for_services(services,device_alias)

        return Response(response=json.dumps({"status":"ok"}), mimetype='application/json')