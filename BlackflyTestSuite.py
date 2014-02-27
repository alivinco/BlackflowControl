from flask import Flask, Response
from flask import render_template
from flask import request
from modules.msg_cache import MsgCache
from modules.msg_manager import MessageManager
import json
app = Flask(__name__)
msg_man = MessageManager()
cache = MsgCache(msg_man)
a = 0


@app.route('/')
def hello_world():
    return 'Hello World 3!'


@app.route('/index')
def index():
    msg_list = msg_man.load_templates()
    return render_template('index.html', msg_list=msg_list)


@app.route('/devices/<name>')
def devices(name):
    mapping = msg_man.generate_linked_mapping(msg_man.load_msg_class_mapping(), msg_man.load_address_mapping())
    return render_template('devices.html', mapping=mapping,cache=cache)

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
    # print json.dumps(command,indent=True)
    cache.put(req["msg_key"].split("@")[1],command)
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
    app.debug = True
    app.run()
