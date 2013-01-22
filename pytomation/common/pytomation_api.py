from .pytomation_object import PytomationObject
from ..common.pytomation_system import *

class PytomationAPI(PytomationObject):
    def get_response(self, method="GET", path=None):
        return get_instances_detail()