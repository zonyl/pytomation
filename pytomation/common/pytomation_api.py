from .pytomation_object import PytomationObject
#from .pytomation_system import *
import pytomation_system
import json
#from collections import OrderedDict

class PytomationAPI(PytomationObject):
    JSON = 'json'

    def get_map(self):
        return {
           ('get','devices'): PytomationAPI.get_devices,
           ('get', 'device'): PytomationAPI.get_device,
           ('post', 'device'): self.update_device,
           }
    
    def get_response(self, method="GET", path=None, type=None, data=None, source=None):
        response = None
        method = method.lower()
        levels = path.split('/')
#        print 'pizz:' + path + "l:" + levels[0] + "DDD"+ str(data)
#	print "eeeeee" + str(source)
        type = type.lower() if type else self.JSON
        f = self.get_map().get((method, levels[0]), None)
        if f:
            response = f(levels, data=data, source=source)
        elif levels[0].lower() == 'device':
            try:
                response = self.update_device(command=method, levels=levels, source=source)
            except Exception, ex:
                pass
        if type==self.JSON:
            return json.dumps(response)
        return None

    @staticmethod
    def get_devices(path=None, *args, **kwargs):
        devices = []
        for (k, v) in pytomation_system.get_instances_detail().iteritems():
            try:
                v.update({'id': k})
                a = v['instance']
                b = a.state
                del v['instance']
#                devices.append({k: v})
                devices.append(v)
            except Exception, ex:
                pass
#        f = OrderedDict(sorted(devices.items()))
#        odevices = OrderedDict(sorted(f.items(), key=lambda k: k[1]['type_name'])
#                            )
        return devices

    @staticmethod
    def get_device(levels, *args, **kwargs):
        id = levels[1]
        detail = pytomation_system.get_instances_detail()[id]
        detail.update({'id': id})
        del detail['instance']
        return detail
    
    def update_device(self, levels, data=None, source=None, *args, **kwargs):
        command = None
#	print 'kkkkkkkk' + str(source)
        if not source:
            source = self

        if data:
            if isinstance(data, list):
                for d in data:
#                    print 'ff' + str(d)
                    e = d.split('=')
#                    print 'eee' + str(e)
                    if e[0]== 'command':
                        command = e[1]
            else:
                e = data.split('=')
                command = e[1]
#        print 'Set Device' + str(command) + ":::" + str(levels)
        id = levels[1]
        try:
            detail = pytomation_system.get_instances_detail()[id]
            device = detail['instance']
            device.command(command=command, source=source)
            response =  PytomationAPI.get_device(levels)
        except Exception, ex:
            pass
#        print 'res['+ str(response)
        return response
