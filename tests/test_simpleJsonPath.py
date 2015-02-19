from unittest import TestCase
from libs.simple_jsonpath import SimpleJsonPath
from modules.msg_manager import MessageManager
__author__ = 'alivinco'


class TestSimpleJsonPath(TestCase):
    def test__get_path_list(self):
        msg_man = MessageManager()
        jpath = SimpleJsonPath()
        msg = msg_man.load_template_by_key("zw_ta.inclusion_report@event")

        r = jpath.get(msg,"$.event.default.value.[1]")
        print r
        r = jpath.get(msg,"$.event.default.value.[1]")
        print r

        # print msg