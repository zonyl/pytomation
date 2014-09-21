from .pytomation_object import PytomationObject
#from .pytomation_system import *
import pytomation_system
import json
import urllib
#from collections import OrderedDict

class PytomationAPI(PytomationObject):
    VERSION = '2.0'
    JSON = 'json'
    WEBSOCKET = 'websocket'

    def get_map(self):
        return {
                   ('get', 'devices'): PytomationAPI.get_devices,
                   ('get', 'device'): PytomationAPI.get_device,
                   ('post', 'device'): self.update_device,
        }

    def get_response(self, method="GET", path=None, type=None, data=None, source=None):
        response = None
        type = type.lower() if type else self.JSON
        method = method.lower()
        levels = path.split('/')
        if data:
            if isinstance(data, list):
                tdata = []
                for i in data:
                    tdata.append(urllib.unquote(i).decode('utf8'))
                data = tdata
            else:
                data = urllib.unquote(data).decode('utf8')

        f = self.get_map().get((method, levels[0]), None)
        if f:
            response = f(levels, data=data, source=source)
        elif levels[0].lower() == 'device':
            try:
                response = self.update_device(command=method, levels=levels, source=source)
            except Exception, ex:
                pass
        if type == self.JSON:
            return json.dumps(response)
        elif type == self.WEBSOCKET:
            if method != 'post':
                return json.dumps(response)
            else:
                return json.dumps("success")
        return None

    def get_state_changed_message(self, state, source, prev, device):
        return json.dumps({
            'id': device.type_id,
            'name': device.name,
            'type_name': device.type_name,
            'state': state,
            'previous_state': prev
        })

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
        detail = pytomation_system.get_instance_detail(id)
        detail.update({'id': id})
        del detail['instance']
        return detail
    
    def update_device(self, levels, data=None, source=None, *args, **kwargs):
        command = None
        response = None
        if not source:
            source = self

        if data:
            if isinstance(data, list):
                for d in data:
#                    print 'ff' + str(d)
                    e = d.split('=')
#                    print 'eee' + str(e)
                    if e[0] == 'command':
                        command = e[1]
            else:
                e = data.split('=')
                command = e[1]
#        print 'Set Device' + str(command) + ":::" + str(levels)
        id = levels[1]
        # look for tuples in the command and make it a tuple
        if ',' in command:
            e = command.split(',')
            l = []
            # lets convert any strings to int's if we can
            for i in e:
                t = i
                try:
                    t = int(i)
                except:
                    pass
                l.append(t)
            command = tuple(l)
        try:
            detail = pytomation_system.get_instances_detail()[id]
            device = detail['instance']
            device.command(command=command, source=source)
            response = PytomationAPI.get_device(levels)
        except Exception, ex:
            pass
#        print 'res['+ str(response)
        return response
