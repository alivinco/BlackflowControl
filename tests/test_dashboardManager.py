from unittest import TestCase
from modules.mod_dashboards import DashboardManager
from modules.msg_manager import MessageManager

__author__ = 'alivinco'


class TestDashboardManager(TestCase):

    def setUp(self):
        self.dm = DashboardManager()
        self.msg_man = MessageManager()

    def test_add_service_to_dashboard(self):

        self.dm.add_service_to_dashboard("dash1","default","122")

        # self.fail()

    def test_generate_linked_mapping(self):
        linked_map = self.msg_man.generate_linked_mapping(self.msg_man.msg_class_mapping, self.msg_man.address_mapping)
        if len(linked_map)>0:
            print "Ok"
        else :self.fail()

    def test_get_dashboard_grid_size(self):
        self.dm.get_dashboard_grid_size("dash1")

