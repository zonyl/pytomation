from .pytomation_object import PytomationObject
from ..utility.periodic_timer import PeriodicTimer
from ..utility.manhole import Manhole

def get_instances():
    return PytomationObject.instances

def get_instances_detail():
    details = {}
    for object in get_instances():
        details.update({
                       object.type_id: {
                                   'instance': object,
                                   'name': object.name,
                                   'type_name': object.type_name,
                                   } 
                       })
        
    return details

def start(loop_action=None, loop_time=1, admin_user=None, admin_password=None, telnet_port=2000):
    if loop_action:
        myLooper = PeriodicTimer(loop_time) # loop every 1 sec
        myLooper.action(loop_action)
        myLooper.start()
    
    if admin_user:
        Manhole().start(user=admin_user, password=admin_password, port=telnet_port, instances=get_instances_detail())
    
    
