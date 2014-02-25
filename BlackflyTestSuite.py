from flask import Flask
from flask import render_template
from modules.msg_manager import MessageManager
app = Flask(__name__)
msg_man = MessageManager()
a = 0

@app.route('/')
def hello_world():
    return 'Hello World 3!'
@app.route('/index')
def index():

    msg_list = msg_man.list_files()
    return render_template('index.html', msg_list=msg_list)


if __name__ == '__main__':
    app.debug = True
    app.run()
