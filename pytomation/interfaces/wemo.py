from pytomation.utility.miranda import upnp
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
    def __init__(self, ip, port=None, *args, **kwargs):
        self._ip = ip
        self._port = port
        super(WeMo, self).__init__(None, *args, **kwargs)
    
    def _setstate(self, state):
        conn = upnp()
        #print 'uuuuu - {0}:{1}'.format(self._ip, self._port)
        try:
            resp = conn.sendSOAP('{0}:{1}'.format(self._ip, self._port),
                                'urn:Belkin:service:basicevent:1', 
                                'http://{0}:{1}/upnp/control/basicevent1'.format(self._ip, self._port), 
             'SetBinaryState', {'BinaryState': (state, 'Boolean')})
        except Exception, ex:
            self._logger.error('Error trying to send command: '+ str(ex))
            
        return resp

    def on(self, *args, **kwargs):
        self._setstate(1)
        
    def off(self, *args, **kwargs):
        self._setstate(0)