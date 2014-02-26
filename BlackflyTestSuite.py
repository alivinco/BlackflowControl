from flask import Flask, Response
from flask import render_template
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
    return render_template('devices.html', mapping=mapping)

@app.route('/api/send_command')
def send_command():

    #it has to contain key = switch_binary@.zw.7.binary_switch.2.commands and value
    # then it will be combined with message template and final message generated
    # add to cache 
    dev = json.dumps({"result":"ok"})
    response = Response(response=dev, mimetype='application/json' )

@app.route('/api/get_events')
def get_events():
    dev = json.dumps({"result":"ok"})
    return Response(response=dev, mimetype='application/json' )


if __name__ == '__main__':
    app.debug = True
    app.run()
