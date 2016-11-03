#  Aleksandrs Livincovs <aleksandrs.livincovs@gmail.com>
import argparse , os
import json
import uuid
from flask import Flask, Response, redirect, url_for, send_from_directory
from flask import render_template
from flask import request
import time

from libs import utils
from libs.flask_login import LoginManager, login_required
from libs.utils import format_iso_time_from_sec , gen_sid, convert_bool
# import modules
from modules.mod_containers import ServiceDiscovery
from modules.mod_tools import Tools
# Flask initialization
import configs.log
import logging, logging.config
from os import environ as env
from libs.sync_to_async_msg_converter import SyncToAsyncMsgConverter
from extensions.auth.ui import controller as auth_ex
from extensions.auth.ui.controller import mod_auth, login_manager
from extensions.blackflow.ui import controller as blackflow_ex
from configs import globals
import mimetypes

mimetypes.add_type('image/svg+xml', '.svg')

# Global variables
from modules.mqtt_adapter import MqttAdapter

instance_name = "blackflow"
auth_ex.APP_INSTANCE = instance_name
root_uri = "/"+instance_name
app = None
http_server_port = None
global_context = {}
msg_man = None

mqtt = None
conf = dict()
conf_path = ""
sync_async_client = None
bf_containers = None
# Msg api wrappers message wrapper
log = logging.getLogger("bf_web")


def init_app_components():
    # uri root prefix
    global root_uri, http_server_port
    global app, global_context
    global mqtt, sync_async_client , conf , conf_path, bf_containers

    logging.config.dictConfig(configs.log.config)
    log.info("Checking firewall configuration")
    log.info(Tools.open_port_in_firewall())
    # Injecting root uri prefix
    mod_auth.url_prefix = root_uri
    login_manager.login_view = globals.get_full_url("/ui/login")
    log.debug("Login view url = %s" % login_manager.login_view)
    blackflow_ex.blackflow_bp.url_prefix = root_uri

    # Check and init application/service ID (sid)
    if not conf["system"]["sid"]:
        # the id is base on MAC address , which means it may not be unique
        sid = gen_sid()
        conf["system"]["sid"] = sid
        utils.save_config(conf_path,conf)
    else:
        sid = conf["system"]["sid"]

    # Flask init
    app = Flask(__name__)
    secret_key = ""
    try :
        secret_file = open("secret.db","r")
        secret_key = secret_file.read()
        secret_file.close()
    except IOError :
        import os
        secret_file = open("secret.db","w")
        secret_key = str(os.urandom(24))
        secret_file.write(secret_key)
        secret_file.close()
    # app.secret_key = '\xb5\xd4\xa1\xa5_\xc9\x07"\xaa\xb5\x1d1\xea\xd0\x08\\\xe9\x0b\x056\xf9J\x8f\xd0'
    app.secret_key = secret_key
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_FILE_DIR'] = '/tmp/'
    app.config['SESSION_COOKIE_NAME'] = 'bflowctr'
    app.config['LOGIN_DISABLED'] = conf["system"]["ui_security_disabled"]
    # app.config['APPLICATION_ROOT'] = root_uri
    app.register_blueprint(mod_auth)
    app.register_blueprint(blackflow_ex.blackflow_bp)
    login_manager.init_app(app)

    http_server_port = conf["system"]["http_server_port"]
    # Influx DB
    # Mqtt Adapter
    mqtt = MqttAdapter(conf["mqtt"]["client_id"])
    mqtt.set_mqtt_params(conf["mqtt"]["client_id"], conf["mqtt"]["username"], conf["mqtt"]["password"],
                         conf["mqtt"]["global_topic_prefix"], conf["mqtt"]["enable_sys"])
    mqtt.set_global_context(global_context)
    try:
        if mqtt.connect(conf["mqtt"]["host"], int(conf["mqtt"]["port"])):
            mqtt.start()
        else:
            global_context['mqtt_conn_status'] = "offline"
            log.error("application can't connect to message broker.")
    except Exception as ex:
        global_context['mqtt_conn_status'] = "offline"
        log.error("application can't connect to message broker.")
        log.error(ex)

    # Sync async which implement sync service invocation over async
    sync_async_client = SyncToAsyncMsgConverter(mqtt)
    mqtt.set_message_handler(sync_async_client.on_message)
    auth_ex.global_context = global_context
    if global_context["auth_type"] == "local":
        auth_ex.um.load_from_storage()
    bf_containers = ServiceDiscovery(sync_async_client)

    blackflow_ex.global_context = global_context
    blackflow_ex.sync_async_client = sync_async_client
    blackflow_ex.svc_discovery = bf_containers


def init_controllers():
    @app.route(root_uri + '/static/<path:path>')
    def send_js(path):
        return send_from_directory('static', path)

    @app.route(root_uri +'/')
    def root_page():
        return redirect(globals.get_full_url("/ui/index"))

    @app.route(root_uri + '/ui/index')
    @login_required
    def index():
        return render_template('index.html', global_context=global_context)

    @app.route(root_uri + '/ui/settings', methods=["POST", "GET"])
    @login_required
    def settings_ui():
        if request.method == 'POST':
            conf["system"]["sid"] = request.form["system_sid"]

            conf["mqtt"]["host"] = request.form["mqtt_host"]
            conf["mqtt"]["port"] = request.form["mqtt_port"]
            conf["mqtt"]["client_id"] = request.form["mqtt_client_id"]
            conf["mqtt"]["username"] = request.form["mqtt_username"]
            conf["mqtt"]["password"] = request.form["mqtt_password"]
            conf["mqtt"]["global_topic_prefix"] = request.form["mqtt_global_topic_prefix"]
            conf["mqtt"]["enable_sys"] = convert_bool(request.form["enable_sys"])

            mqtt.set_mqtt_params(request.form["mqtt_client_id"], request.form["mqtt_username"], request.form["mqtt_password"], request.form["mqtt_global_topic_prefix"],
                                 conf["mqtt"]["enable_sys"])

            utils.save_config(conf_path, conf)

            log.info("Global config was successfully updated")
            log.info("New values are mqtt host = " + request.form["mqtt_host"] + " port = " + request.form["mqtt_port"] + " root topic = " + " client id=" + request.form["mqtt_client_id"])

        return render_template('settings.html', cfg=conf, global_context=global_context)

    @app.route(root_uri + '/ui/help/<page>')
    @login_required
    def help(page):
        return render_template('help_' + page + '.html', cfg=conf, global_context=global_context)

    @app.route(root_uri + '/api/wait_for_msg', methods=["POST", "GET"])
    @login_required
    def wait_for_msg():
        topic = request.args.get("topic")
        timeout = int(request.args.get("timeout", 30))
        # MSG_TYPE or NO_COR_ID
        cor_type = request.args.get("correlation_type", "MSG_TYPE")
        msg_type = request.args.get("msg_type")
        msg = sync_async_client.sync_wait_for_msg(topic, cor_type, msg_type, timeout)
        jobj = json.dumps(msg)
        return Response(response=jobj, mimetype='application/json')

    @app.route(root_uri + '/ui/tools', methods=["POST", "GET"])
    @login_required
    def tools():
        tools = Tools()
        output = ""
        services = []
        logs = []
        try:
            if request.method == "POST":
                action = request.form["action"]
                log.info("Tools request.action=" + action)
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
        except Exception as ex:
            output = str(ex)

        return render_template('tools.html', output=output, global_context=global_context, logs=logs, services=services, autoescape=False)

    @app.route(root_uri + '/ui/updates', methods=["POST", "GET"])
    @login_required
    def updates():
        import urllib2
        import os

        distro_uri = conf["system"]["distro_server_uri"]
        platform = conf["system"]["platform"]
        build_info_path = os.path.join(os.getcwd(), "configs", "build_info.json")
        current_info = json.load(file(build_info_path))
        develop_info = json.load(urllib2.urlopen(distro_uri + "/develop/build_info.json", timeout=15))
        master_info = json.load(urllib2.urlopen(distro_uri + "/build_info.json", timeout=15))
        log.debug(develop_info)
        log.debug(master_info)
        status = ""
        if request.method == "POST":
            tools = Tools()
            action = request.form["action"]
            if action == "update_to_master":
                tools.run_update_procedure(distro_uri, platform)
            if action == "update_to_develop":
                tools.run_update_procedure(distro_uri + "/develop", platform)
            status = "Update procedure is in progres..... please check /var/log/blackfly_upgrade.log for details "

        return render_template('updates.html', global_context=global_context, current_info=current_info, develop_info=develop_info, master_info=master_info,
                               autoescape=False, status=status)

    @app.route(root_uri + '/ui/logviewer', methods=["POST", "GET"])
    @login_required
    def log_viewer():
        tools = Tools()
        log_file = request.form["log_file"]
        tail_size = request.form["tail_size"]
        search = request.form["search"]

        output = tools.tail_log(log_file, int(tail_size), search)
        output = "<pre>" + output + "</pre>"
        return output

    @app.route(root_uri + '/ui/mqtt_client', methods=["POST", "GET"])
    @login_required
    def mqtt_client():
        status = ""
        address = ""
        if request.method == "GET":
            payload = {"origin": {"@id": "blackfly", "@type": "app"},
                       "uuid": str(uuid.uuid4()),
                       "creation_time": int(time.time() * 1000),
                       "command": {"default": {"value": "__fill_me__"}, "subtype": "__fill_me__", "@type": "__fill_me__"},
                       "spid": "SP1",
                       }
            payload = json.dumps(payload, indent=True)
            return render_template('mqtt_client.html', global_context=global_context, address=address, payload=payload, status=status)

        if request.method == "POST":
            address = request.form["address"]
            payload = request.form["payload"]
            log.info(type(payload))
            log.info("Payload" + str(payload))
            mqtt.publish(address, str(payload), 1)
            return Response(response="{}", mimetype='application/json')

    @app.route(root_uri + '/sys/mqtt_ctrl/<command>')
    @login_required
    def mqtt_control(command):
        if command == "start":

            try:
                if global_context['mqtt_conn_status']=="offline" or global_context['mqtt_conn_status']=="reconnecting":
                    if mqtt.connect(conf["mqtt"]["host"], int(conf["mqtt"]["port"])):
                        mqtt.start()
                        status = "Connected to broker."
                    else :
                        status = "Can't connect to broker."
                else:
                    log.info("The system is already connected to mqtt broker.")
                    status = "Start command was skiped . The system is already connected to mqtt broker."
            except Exception as ex:
                log.error("Can't connect to server because of error:")
                log.error(ex)
                status = "Can't connect to broker"

        elif command == "stop":
            mqtt.stop()
            status = "Disconnected from broker"

        # dev = json.dumps({"success":True})
        # return Response(response=dev, mimetype='application/json' )
        return render_template('mqtt_status.html', status=status, global_context=global_context)

    @app.route(root_uri + '/ui/config_editor', methods=["POST", "GET"])
    @login_required
    def config_editor():
        status = ""
        if request.method == "POST":
            address = request.form["address"]
            payload = request.form["payload"]
            log.info(type(payload))
            log.info("Payload" + str(payload))
            mqtt.publish(address, str(payload), 1)
            status = "The message was sent"

        return render_template('config_editor.html', global_context=global_context, status=status)


def configure():
    global conf,root_uri, instance_name,global_context
    parser = argparse.ArgumentParser()
    parser.add_argument('-c','--conf', help='Config file path')
    parser.add_argument('-acli','--authclientid', help='Auth0 application client id')
    parser.add_argument('-acsec','--authclientsecret', help='Auth0 client secret')
    parser.add_argument('-acredir','--authredirect', help='Auth0 redirect ui')
    parser.add_argument('-rurl','--rooturl', help='Application root url')
    args = parser.parse_args()
    globals.AUTH0_CLIENT_ID = args.authclientid
    globals.AUTH0_CLIENT_SECRET = args.authclientsecret
    conf_path = args.conf
    conf = utils.load_config(conf_path)
    # ENV variables set by BlackTower automatically
    if env.get("ZM_MQTT_BROKER_ADDR"):
        add_split = env.get("ZM_MQTT_BROKER_ADDR").split(":")
        conf["mqtt"]["host"] = add_split[0]
        if len(add_split) == 2:
            conf["mqtt"]["port"] = add_split[1]
    if env.get("ZM_MQTT_USERNAME"):
        conf["mqtt"]["username"] = env.get("ZM_MQTT_USERNAME")
    if env.get("ZM_MQTT_PASSWORD"):
        conf["mqtt"]["password"] = env.get("ZM_MQTT_PASSWORD")
    if env.get("ZM_MQTT_CLIENTID"):
        conf["mqtt"]["client_id"] = env.get("ZM_MQTT_CLIENTID")
    if env.get("ZM_APP_INSTANCE"):
        instance_name = env.get("ZM_APP_INSTANCE")
        globals.APP_INSTANCE = instance_name
        root_uri = "/"+instance_name
        global_context["root_uri"] = root_uri
    if env.get("ZM_DOMAIN"):
        conf["mqtt"]["global_topic_prefix"] = env.get("ZM_DOMAIN")

    # ENV variables set by BlackTower but have to be set manually per app .
    if env.get("ZW_APP_AUTH_CLIENT_ID"):
        globals.AUTH0_CLIENT_ID = env.get("ZW_APP_AUTH_CLIENT_ID")
    if env.get("ZW_APP_AUTH_CLIENT_SECRET"):
        globals.AUTH0_CLIENT_SECRET = env.get("ZW_APP_AUTH_CLIENT_SECRET")
    if env.get("ZW_APP_AUTH_REDIRECT_URI"):
        globals.REDIRECT_URI = env.get("ZW_APP_AUTH_REDIRECT_URI")
    elif args.authredirect :
        globals.REDIRECT_URI = args.authredirect
    else:
        globals.REDIRECT_URI = "/blacktower/applogincallback"
    if env.get("ZW_APP_HTTP_ROOT_URL"):
        globals.ROOT_URL = env.get("ZW_APP_HTTP_ROOT_URL")
    elif args.rooturl :
        globals.ROOT_URL = args.rooturl
    else :
        globals.ROOT_URL = conf["system"]["http_root_url"]
    globals.ROOT_URL = "%s/%s" % (globals.ROOT_URL, globals.APP_INSTANCE)
    global_context["version"] = conf["system"]["version"]
    global_context["root_uri"] = root_uri
    global_context["app_store_api_url"] = conf["app_store"]["api_url"]
    global_context["app_store_username"] = conf["app_store"]["username"]
    global_context["auth_type"] = conf["system"]["auth_type"]


if __name__ == '__main__':
    configure()
    configs.log.config["handlers"]["info_file_handler"]["filename"] = os.path.join(conf["log_dir"], "blackflowctrl_info.log")
    configs.log.config["handlers"]["error_file_handler"]["filename"] = os.path.join(conf["log_dir"], "blackflowctrl_error.log")
    logging.config.dictConfig(configs.log.config)
    log.info("App HTTP full root url = %s" % globals.ROOT_URL)
    init_app_components()
    init_controllers()
    app.run(host="0.0.0.0", port=http_server_port, debug=True, use_debugger=True, threaded=True, use_reloader=False)
