import time
import mosquitto

__author__ = 'alivinco'


from greenlet import greenlet


class MqttAdapter():
    def __init__(self):
        self.mqtt = mosquitto.Mosquitto(self.client_id, clean_session=True)
        self.registered_flows = {}

    def _on_message(self, mosq, obj, msg):
        self.mqtt.on_message = self._on_message




def test1():
    print 12
    gr2.switch()
    print 34

def test2():
    print 56
    gr1.switch()
    print 78

def on_msg(addr,flow_id):
    print "waiting for message"
    time.sleep(5)
    return "motion detected"

def sending():
    pass

def activate_mode(name):
    print "activating mode "+name

def flow_1():
    flow_id = 1
    print "execution main flow"
    # subscribing for event and waiting
    motion = receive.switch("/dev/motion",flow_id)
    print motion
    # subscribing for another event and waiting
    open = receive.switch("/dev/bin_open",flow_id)
    activate_mode("ARM")


gr1 = greenlet(test1)
gr2 = greenlet(test2)
gr1.switch()

flow_1_g = greenlet(flow_1)

receive = greenlet(on_msg)
