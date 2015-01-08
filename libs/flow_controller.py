__author__ = 'alivinco'

class FlowInstance():
    def __init__(self,id,name,trigger_topic,msg_type,correlation_func_ref):
        self.id = name
        self.name =  name
        self.trigger_topic = trigger_topic
        self.msg_type = msg_type
        self.correlation_func = correlation_func_ref


class FlowController():
    # Table contains flow metadata
    flow_table = {}
    # Table contains all active flow instances
    instance_table = []
    # Table contains waiting "receives" and definition which can resume flow executions
    receive_table = []

    def __init__(self):
        pass

    def on_message(self,topic,payload):
        pass

    # def