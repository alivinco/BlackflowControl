from libs.dmapi.core import Core

__author__ = 'alivinco'

class Blackflow(Core):
    def context_get(self):
        return self.get_message("command","blackflow.context_get")

    def get_apps(self):
        return self.get_message("command","blackflow.get_apps")

    def get_app_instances(self):
        return self.get_message("command","blackflow.get_app_instances")

    def get_analytics(self):
        return self.get_message("command","blackflow.analytics_get")



