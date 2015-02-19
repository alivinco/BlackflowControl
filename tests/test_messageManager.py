from unittest import TestCase
from libs.simple_jsonpath import SimpleJsonPath
from modules.msg_manager import MessageManager
import time

__author__ = 'alivinco'


class TestMessageManager(TestCase):

    def setUp(self):
        self.msg_man = MessageManager()

    def test_get_value_from_msg(self):
        msg = self.msg_man.load_template_by_key("sensor.temperature@event")
        st = time.time()
        run_count = 50000
        for i in range(run_count):
             value =  self.msg_man.get_value_from_msg(msg,"$.event.default.value")[0]
        et = time.time()
        print "Test 1.0 using jsonpath as it is, execution time %s"%(et-st)

        ##########################################################
        st = time.time()
        jpath = "$.event.default.value"
        el_names = jpath.split(".")
        for i in range(run_count):
            next_item = msg
            for item in el_names[1:]:
                next_item = next_item[item]
            # print "Result is %s"%next_item
        et = time.time()
        print "Test 2.0 execution time %s"%(et-st)
         ##########################################################
        st = time.time()
        jpath = "$.event.default.value"

        for i in range(run_count):
            next_item = msg
            el_names = jpath.split(".")
            for item in el_names[1:]:
                next_item = next_item[item]
            # print "Result is %s"%next_item
        et = time.time()
        print "Test 2.5 execution time %s"%(et-st)
        ##########################################################

        jpath = "$.event.default.value"
        el_names = jpath.split(".")
        el_names_map={}
        el_names_map[jpath] = el_names
        # filling in map with dummy data
        for i in range(30):
            el_names_map[jpath+str(i)] = "dsafgdsagasdgsadgagsfgs"
        st = time.time()
        for i in range(run_count):
            next_item = msg
            for item in el_names_map[jpath][1:]:
                next_item = next_item[item]
            # print "Result is %s"%next_item
        et = time.time()

        print "Test 3.0 execution time %s"%(et-st)
        ##########################################################

        st = time.time()
        for i in range(run_count):
            value =  msg["event"]["default"]["value"]
        et = time.time()
        print "Test 4.0 execution time %s"%(et-st)

        ##############################################################
        jp = SimpleJsonPath()
        jp.get(msg,jpath)
        st = time.time()
        for i in range(run_count):
            value =  jp.get(msg,jpath)

        et = time.time()
        print "Test 5.0 execution time %s"%(et-st)