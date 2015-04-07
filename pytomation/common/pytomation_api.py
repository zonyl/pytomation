from .pytomation_object import PytomationObject
#from .pytomation_system import *
import pytomation_system
import json
import urllib
#from collections import OrderedDict

class PytomationAPI(PytomationObject):
    VERSION = '3.0'
    Provides a REST WebAPI for Pytomation.
    """
    JSON = 'json'
    WEBSOCKET = 'websocket'

    def get_map(self):
        return {
                   ('get', 'devices'): PytomationAPI.get_devices,
                   ('get', 'device'): PytomationAPI.get_device,
                   ('post', 'device'): self.update_device,
                   ('post', 'voice'): self.run_voice_command
        }
        
    def run_voice_command(self, levels, data, source):
        for command in data:
            command =  command.lower()
            for dev_name in self.sorted_names_by_length:
                if command.find(dev_name) != -1:
                    #remove the name from command so it doesn't interfere
                    #with the next search
                    command = command.replace(dev_name,'')
                    dev_id = self.name_to_id_map[dev_name]
                    device = self.instances[dev_id]
                    levels = ['device', dev_id]
                    for device_command in device.COMMANDS:
                        if command.find(device_command) != -1:
                            command = command.replace(device_command,'')
                            try:
                                numeric_command = ''.join(ele for ele in command if ele.isdigit())
                                if numeric_command:
                                    device_command = device_command + ',' + numeric_command
                            except:
                                pass
                            return self.update_device(levels, 'command=' + device_command, source)
                    try:
                        numeric_command = ''.join(ele for ele in command if ele.isdigit())
                        if numeric_command:
                            device_command = device.DEFAULT_NUMERIC_COMMAND + ',' + numeric_command
                            return self.update_device(levels, 'command=' + device_command, source)
                        else:
                            return self.update_device(levels, 'command=' + device.DEFAULT_COMMAND, source)
                    except:
                        return self.update_device(levels, 'command=' + device.DEFAULT_COMMAND, source)
        #Maybe we should ask the internet from here?
        return json.dumps("I'm sorry, can you please repeat that?") 

    def get_response(self, method="GET", path=None, type=None, data=None, source=None):
        response = None
        type = type.lower() if type else self.JSON
        if type == self.WEBSOCKET:
            try:
                data = json.loads(data)
            except Exception, ex:
                pass
            
            path = data['path']
            
            try:
                data = data['command']
                if path != 'voice':
                    data = 'command=' + data if data else None
            except Exception, ex:
                #If no command just send back data being requested
                data = None
                type = self.JSON
            method = "post" if data else "get"
        elif path == 'voice':
            data = urllib.unquote(data).replace('&', '').replace('+', ' ').split("command[]=")
            
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
        """
        Returns all devices and status in JSON.
        """
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
        """
        Returns one device's status in JSON.
        """
        id = levels[1]
        detail = pytomation_system.get_instance_detail(id)
        detail.update({'id': id})
        del detail['instance']
        return detail
    
    def update_device(self, levels, data=None, source=None, *args, **kwargs):
        """
        Issues command in POST from JSON format.
        """
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
