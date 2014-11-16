import time
import select
from .pytomation_object import PytomationObject
from ..utility.periodic_timer import PeriodicTimer
#from ..utility.manhole import Manhole
from ..utility.http_server import PytomationHTTPServer

def get_instances():
    return PytomationObject.instances

def get_instances_detail():
    details = {}
    for object in PytomationObject.instances.itervalues():
        object_detail = {'instance': object,
                         'name': object.name,
                         'type_name': object.type_name,
                         }
        try:
            object_detail.update({'commands': object.COMMANDS})
            object_detail.update({'state': object.state})
            object_detail.update({'devices': object.device_list()})
        except Exception, ex:
            # Not a state device
            pass
        details.update({
                       object.type_id: object_detail,
                       })
        
    return details

def get_instance_detail(object_id):
    object = PytomationObject.instances[object_id]
    object_detail = {'instance': object,
                     'name': object.name,
                     'type_name': object.type_name,
                     }
    try:
        object_detail.update({'commands': object.COMMANDS})
        object_detail.update({'state': object.state})
        object_detail.update({'devices': object.device_list()})
    except Exception, ex:
        # Not a state device
        pass

    return object_detail

def start(loop_action=None, loop_time=1, admin_user=None, admin_password=None, telnet_port=None, 
          http_address=None, http_port=None, http_path=None):
    if loop_action:
        # run the loop for startup once
        loop_action(startup=True)
        # run periodically from now on
        myLooper = PeriodicTimer(loop_time) # loop every 1 sec
        myLooper.action(loop_action, None, {'startup': False} )
        myLooper.start()
    
    if telnet_port:
        Manhole().start(user=admin_user, password=admin_password, port=telnet_port, instances=get_instances_detail())

    if http_address and http_port and http_path and False:
        PytomationHTTPServer(address=http_address, port=http_port, path=http_path).start()
    else:
        # sit and spin - Let the magic flow
        #select.select([],[],[])
        while True: time.sleep(1)
