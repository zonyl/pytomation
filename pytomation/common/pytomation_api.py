from .pytomation_object import PytomationObject
#from .pytomation_system import *
import pytomation_system

class PytomationAPI(PytomationObject):
    def get_response(self, method="GET", path=None):
        return pytomation_system.get_instances_detail()
