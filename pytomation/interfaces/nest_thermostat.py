"""
Nest Thermostat Pytomation Interface

Author(s):
Jason Sharpee
jason@sharpee.com

Library used from:
Jeffrey C. Ollie
https://github.com/jcollie/pyenest

"""
import json
import re
import time
try:
    from pyjnest import Connection
except Exception, ex:
    pass

from .ha_interface import HAInterface
from .common import *

class NestThermostat(HAInterface):
    VERSION = '1.0.0'
    
    def __init__(self, *args, **kwargs):
        super(NestThermostat, self).__init__(None, *args, **kwargs)
        
    def _init(self, *args, **kwargs):
        super(NestThermostat, self)._init(*args, **kwargs)
        self._last_temp = None
        self._mode = None
        self._hold = None
        self._fan = None
        self._set_point = None
        self._away = None
        
        self._user_name = kwargs.get('username', None)
        self._password = kwargs.get('password', None)
        self._iteration = 0
        self._poll_secs = kwargs.get('poll', 60)
        

        self.interface = Connection(self._user_name, self._password)
        try:
            self.interface.login()
        except Exception, ex:
            self._logger.debug('Could not login: ' + str(ex))
        
        
    def _readInterface(self, lastPacketHash):
        # We need to dial back how often we check the thermostat.. Lets not bombard it!
        if not self._iteration < self._poll_secs:
            self._logger.debug('Retrieving status from thermostat.')
            self._iteration = 0
            #check to see if there is anything we need to read
            try:
                self.interface.update_status()
                for device in self.interface.devices.values():
                    print device
                    c_temp = device.current_temperature
                    temp = int(9.0/5.0 * c_temp + 32)
                    if self._last_temp != temp:
                        self._last_temp = temp
                        self._onCommand((Command.LEVEL, temp), device.device_id)
            except Exception, ex:
                self._logger.error('Could not process data from API: '+ str(ex))

        else:
            self._iteration+=1
            time.sleep(1) # one sec iteration
    
    def circulate(self, address, *args, **kwargs):
        self._fan = True
        try:
            self.interface.devices[address].fan_mode = 'on'
        except Exception, ex:
            self._logger.error('Could not toggle fan' + str(ex))

    def still(self, address, *args, **kwargs):
        self._fan = False
        self.interface.devices[address].fan_mode = 'auto'
    
    def occupy(self, address, *args, **kwargs):
        self._away = False
        for structure in self.interface.structures:
            self.interface.structures[structure].away = False

    def vacate(self, address, *args, **kwargs):
        self._away = True
        for structure in self.interface.structures:
            self.interface.structures[structure].away = True

    def setpoint(self, address, level, timeout=2.0):
        self._set_point = level
        try:
            self.interface.devices[address].change_temperature(level)
        except Exception, ex:
            self._logger.error('Error setting temperature {0} for device= {1},{2}: {3} '.format(
                                                                                        level,
                                                                                        address[0],
                                                                                        address[1],
                                                                                        str(ex)))
        return 
    
    def version(self):
        self._logger.info("HW Thermostat Pytomation driver version " + self.VERSION + '\n')
        
