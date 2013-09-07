#from miranda import upnp
from .ha_interface import HAInterface
from .common import *

"""
sourcE: http://www.scriptforge.org/quick-hack-of-the-belkin-wemo-switch/

from miranda import upnp
conn = upnp()
resp = conn.sendSOAP('10.100.200.41:49153', 'urn:Belkin:service:basicevent:1', 
     'http://10.100.200.41:49153/upnp/control/basicevent1', 
     'SetBinaryState', {'BinaryState': (1, 'Boolean')})

"""

class WeMo(HAInterface):
    pass