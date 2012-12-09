from .pytomation_object import PytomationObject

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