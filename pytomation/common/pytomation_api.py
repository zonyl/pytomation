from .pytomation_object import PytomationObject
#from .pytomation_system import *
import pytomation_system
import json

class PytomationAPI(PytomationObject):
    JSON = 'json'

    def get_map(self):
        return {
           ('get','devices'): PytomationAPI.get_devices
           }
    
    def get_response(self, method="GET", path=None, type=None):
        response = None
        levels = path.split('/')
#        print 'pizz:' + path + "l:" + levels[0]
        type = type.lower() if type else self.JSON
        f = self.get_map().get((method.lower(), levels[0]), None)
        if f:
            response = f(levels)
        if type==self.JSON:
            return json.dumps(response)
        return None

    @staticmethod
    def get_devices(path=None):
        instance_names = []
        for (k, v) in pytomation_system.get_instances_detail().iteritems():
            instance_names.append(k)
        return instance_names
