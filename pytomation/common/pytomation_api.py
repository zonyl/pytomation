from .pytomation_object import PytomationObject
#from .pytomation_system import *
import pytomation_system
import json

class PytomationAPI(PytomationObject):
    JSON = 'json'

    def get_map(self):
        return {
           ('get','devices'): PytomationAPI.get_devices,
           ('get', 'device'): PytomationAPI.get_device,
           }
    
    def get_response(self, method="GET", path=None, type=None):
        response = None
        method = method.lower()
        levels = path.split('/')
#        print 'pizz:' + path + "l:" + levels[0]
        type = type.lower() if type else self.JSON
        f = self.get_map().get((method, levels[0]), None)
        if f:
            response = f(levels)
        elif levels[0].lower() == 'device':
            try:
                response = self.set_device(command=method, levels=levels)
            except Exception, ex:
                pass
        if type==self.JSON:
            return json.dumps(response)
        return None

    @staticmethod
    def get_devices(path=None):
        devices = {}
        for (k, v) in pytomation_system.get_instances_detail().iteritems():
            try:
                del v['instance']
                devices.update({k: v})
            except Exception, ex:
                pass
        return devices

    @staticmethod
    def get_device(levels):
        id = levels[1]
        detail = pytomation_system.get_instances_detail()[id]
        del detail['instance']
        return {id: detail}
    
    def set_device(self, command, levels):
        id = levels[1]
        detail = pytomation_system.get_instances_detail()[id]
        device = detail['instance']
        device.command(command=command, source=self)
        response =  PytomationAPI.get_device(levels)
        return response