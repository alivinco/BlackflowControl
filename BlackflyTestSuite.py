from flask import Flask, Response
from flask import render_template
from flask import request
from modules.mqtt_adapter import MqttAdapter
from modules.msg_cache import MsgCache
from modules.msg_manager import MessageManager
import json
app = Flask(__name__)
msg_man = MessageManager()
cache = MsgCache(msg_man)

mqtt = MqttAdapter(cache)
mqtt.connect("lego.r", 1883)
mqtt.start()
a = 0


@app.route('/')
def hello_world():
    return 'Hello World 3!'


@app.route('/index')
def index():
    msg_list = msg_man.load_templates()
    return render_template('index.html', msg_list=msg_list)

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
    mapping = msg_man.generate_linked_mapping(msg_man.load_msg_class_mapping(), msg_man.load_address_mapping())
    return render_template('inter_console.html', mapping=mapping,cache=cache)

@app.route('/ui/cache')
def cache_ui():
    # ch = json.dumps(cache.get_all(),indent=True)
    result = {}
    for k,v in cache.get_all().iteritems():
       result[k]=json.dumps(v,indent=True)
    return render_template('cache.html',cache=result)


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
    mqtt.mqtt.publish(address.replace(".","/"),json.dumps(command),1)
    cache.put(address,command)
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

@app.route('/api/get_last_raw_msg/<key>')
def get_last_raw_msg(key):
    result = cache.get_by_key(key)["raw_msg"]
    dev = json.dumps(result)
    return Response(response=dev, mimetype='application/json' )

if __name__ == '__main__':
    app.debug = False
    app.run()
