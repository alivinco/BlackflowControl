import json
import time
import uuid

__author__ = 'alivinco'

class RequestResponseStruct:
    def __init__(self):
        self.request_topic = ""
        self.request_msg = ""
        self.response_topic = ""
        self.correlation_id = ""
        #
        self.response_msg = ""

class SyncToAsyncMsgConverter:
    def __init__(self,msg_subsystem):
        self.request_timeout = 30
        self.request_table = []
        self.msg_system = msg_subsystem
        self.extract_correlation_id = True
        self.wait_loop_delay = 0.01

    def __generate_correlation_id(self):
        return str(uuid.uuid4())

    def __set_correlation_id(self,msg,corrid):
        msg["corid"] = corrid

    def __extract_correlation_id(self,msg,is_request=True):
        if "corid" in msg : return msg["corid"]
        elif "uuid" in msg : return msg["uuid"]
        else:return None

    def __publish_to_msg_system(self,topic,msg):
        self.msg_system.publish(topic,json.dumps(msg),1)

    def get_request_table_size(self):
        return len(self.request_table)

    def send_sync_msg(self,msg,request_topic,response_topic,timeout=30,generate_corrid=False):

        """
        The method sends message over async messaging subsystem and is waiting for response (blocking) .
        The method is executed in callers thread , which means it block the thread . Request and response
        correlated by corrid.
        :param msg:
        :param request_topic:
        :param response_topic:
        :param timeout:
        :return: msg - if success , None - timeout .
        """

        req_row = RequestResponseStruct()
        req_row.request_topic = request_topic
        req_row.response_topic = response_topic
        if generate_corrid :
            req_row.correlation_id = self.__generate_correlation_id()
            self.__set_correlation_id(msg,req_row.correlation_id)
        else :
            req_row.correlation_id = (lambda : self.__extract_correlation_id(msg) if self.extract_correlation_id  else  self.__generate_correlation_id())()
        # adding object reference to list , means , we can still have the object
        self.request_table.append(req_row)
        # publishing message to a queue
        self.__publish_to_msg_system(request_topic,msg)

        run = True
        start_time = time.time()
        while run :
             if req_row.response_msg :
                response_msg = req_row.response_msg
                self.request_table.remove(req_row)
                run = False
                return response_msg
             else:
                execution_time = time.time()-start_time
                if execution_time < timeout:
                    time.sleep(self.wait_loop_delay)
                else :
                    return None


    def on_message(self,topic,msg):
        """
        The method should be invoked by a message processing pipeline code or something else when a new message appears in msg subsystem .

        :param topic:
        :param msg:
        """
        # small optimisation. Skip messages if there are no requests waiting for response.
        if len(self.request_table)>0:
            cor_id = self.__extract_correlation_id(msg,is_request=False)
            if cor_id:
                # print "on_message :Msg correlation id = "+str(cor_id)
                # print "on_message :Response topic is = "+str(topic)
                req_row = filter((lambda row :topic==row.response_topic and cor_id == row.correlation_id),self.request_table)
                if len(req_row)>0:
                    req_row[0].response_msg = msg





















