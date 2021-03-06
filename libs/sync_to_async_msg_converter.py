import copy
import json
import threading
import time
import uuid

__author__ = 'alivinco'


class RequestResponseStruct:
    def __init__(self):
        self.request_topic = ""
        self.request_msg = ""
        self.response_topic = ""
        self.correlation_id = ""
        # entire response message
        self.response_msg = None
        # Flag indicates whether to ex
        self.single_response = True
        # enum(COR_ID,NO_COR_ID,MSG_TYPE)
        # COR_ID - response correlation id field is used for correlation between request and response
        # NO_COR_ID - no correlation is used , first message in response topic will considered as response
        # MSG_TYPE - no correlation id is used . firs message in response topic with given message type will
        # be considered as response .
        self.correlation_type = "COR_ID"


class SyncToAsyncMsgConverter:
    def __init__(self, msg_subsystem):
        self.request_timeout = 30
        self.request_table = []
        self.msg_system = msg_subsystem
        self.extract_correlation_id = True
        self.wait_loop_delay = 0.01
        self.request_table_lock = threading.Lock()

    def __generate_correlation_id(self):
        return str(uuid.uuid4())

    def __set_correlation_id(self, msg, corrid):
        msg["corid"] = corrid

    def __extract_correlation_id(self, msg, is_request=True):
        return msg.get_corid() if msg.get_corid() else msg.get_uuid()

    def __extract_message_type(self, msg):
        return msg.get_msg_class() + "." + msg.get_msg_subclass()

    def __publish_to_msg_system(self, topic, iot_msg):
        self.msg_system.publish(topic, iot_msg, 1)

    def get_request_table_size(self):
        return len(self.request_table)

    def sync_wait_for_msg(self, response_topic,correlation_type="MSG_TYPE", correlation_msg_type="", timeout=30, ):
        req_row = RequestResponseStruct()
        req_row.request_topic = None
        req_row.response_topic = response_topic
        req_row.correlation_type = correlation_type
        req_row.correlation_id = correlation_msg_type
        with self.request_table_lock:
            self.request_table.append(req_row)

        return self.wait(req_row,timeout)

    def send_and_wait_aggregated_response(self, msg, request_topic, response_topic , correlation_msg_type,wait_time=1):
        """
        Method single message and then waits for a given time and combines all received responses into single result .
        THe method is blocking and is executed in callers thread.

        :type msg : IotMsg
        :param msg: message object
        :param request_topic: request topic
        :param response_topic: the topic to listen for responses
        :param wait_time: time in seconds
        :return : list of IotMsg objects .
        """
        req_row = RequestResponseStruct()
        req_row.request_topic = request_topic
        req_row.response_topic = response_topic
        req_row.correlation_type = "MSG_TYPE"
        req_row.correlation_id = correlation_msg_type
        req_row.single_response = False
         # adding object reference to list , means , we can still have the object
        with self.request_table_lock:
            self.request_table.append(req_row)

        self.__publish_to_msg_system(request_topic, msg)
        time.sleep(wait_time)
        result = list()
        for item in list(self.request_table):
            if item.response_topic == response_topic and item.correlation_type == "MSG_TYPE" and item.correlation_id == correlation_msg_type:
                with self.request_table_lock:
                    if item.response_msg:
                        result.append(item.response_msg)
                    self.request_table.remove(item)
        return result


    def send_sync_msg(self, msg, request_topic, response_topic, timeout=30, generate_corrid=False, correlation_type="COR_ID", correlation_msg_type=""):

        """
        The method sends message over async messaging subsystem and is waiting for response (blocking) .
        The method is executed in callers thread , which means it block the thread . Request and response
        correlated by corrid.
        :type msg:IotMsg
        :param msg: message object
        :param request_topic:
        :param response_topic:
        :param timeout:
        :return: msg - if success , None - timeout .
        """

        req_row = RequestResponseStruct()
        req_row.request_topic = request_topic
        req_row.response_topic = response_topic
        req_row.correlation_type = correlation_type

        if correlation_type == "COR_ID":
            if generate_corrid:
                req_row.correlation_id = self.__generate_correlation_id()
                self.__set_correlation_id(msg, req_row.correlation_id)
            else:
                req_row.correlation_id = (lambda: self.__extract_correlation_id(msg) if self.extract_correlation_id  else  self.__generate_correlation_id())()
        elif correlation_type == "MSG_TYPE":
            req_row.correlation_id = correlation_msg_type

        # adding object reference to list , means , we can still have the object
        with self.request_table_lock:
            self.request_table.append(req_row)
        # publishing message to a queue
        self.__publish_to_msg_system(request_topic, msg)
        print "Request table size = " + str(len(self.request_table))
        return self.wait(req_row, timeout)

    def wait(self, req_row, timeout):
        run = True
        start_time = time.time()
        while run:
            if req_row.response_msg:
                response_msg = req_row.response_msg
                with self.request_table_lock:
                    self.request_table.remove(req_row)
                run = False
                return response_msg
            else:
                execution_time = time.time() - start_time
                if execution_time < timeout:
                    time.sleep(self.wait_loop_delay)
                else:
                    self.request_table.remove(req_row)
                    return None

    def on_message(self, topic, msg):
        """
        The method should be invoked by a message processing pipeline code or something else when a new message appears in msg subsystem .
        It iterates over request_table and is looking for message which correlates with msg .

        :param topic:
        :param msg: msg as json object
        """
        topic_is_in_table = False
        # small optimisation. Skip messages if there are no requests waiting for response.
        if len(self.request_table) > 0:
            # Doing a check if request table has any entry with such topic
            with self.request_table_lock:
                req_rows_with_topic = filter((lambda row: topic == row.response_topic), self.request_table)
                for req_row in req_rows_with_topic:
                    if req_row.correlation_type == "COR_ID":
                        extr_corr_id = self.__extract_correlation_id(msg, is_request=False)
                        if extr_corr_id:
                            if extr_corr_id == req_row.correlation_id:
                                req_row.response_msg = msg
                    elif req_row.correlation_type == "MSG_TYPE":
                        extr_msg_type = self.__extract_message_type(msg)
                        if extr_msg_type:
                            if extr_msg_type == req_row.correlation_id:
                                if req_row.single_response:
                                    req_row.response_msg = msg
                                else:
                                    if not req_row.response_msg:
                                        self.request_table.append(copy.copy(req_row))
                                        req_row.response_msg = msg

                    elif req_row.correlation_type == "NO_COR_ID":
                        req_row.response_msg = msg
