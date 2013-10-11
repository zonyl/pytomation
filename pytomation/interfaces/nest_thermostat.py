"""
Nest Thermostat Pytomation Interface

API:
https://github.com/eae/pyenest/blob/master/pyenest/__init__.py


Author(s):
Jason Sharpee
jason@sharpee.com

Library used from:
Eugene Efremov
https://github.com/eae/pyenest/tree/master/pyenest

"""
import json
import re
import time
from pyenest import Nest

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
        

        self.interface = Nest(self._user_name, self._password)
        try:
            self.interface.login()
        except Exception, ex:
            self._logger.debug('Could not login: ' + str(ex))
        
        
    def _readInterface(self, lastPacketHash):
        # We need to dial back how often we check the thermostat.. Lets not bombard it!
        if not self._iteration < self._poll_secs:
            self._iteration = 0
            #check to see if there is anyting we need to read
            status = self.interface.simple_status
        else:
            self._iteration+=1
            time.sleep(1) # one sec iteration
    
    def circulate(self, address, *args, **kwargs):
        self._fan = True
        try:
            self.interface.toggle_fan(address[0], address[1])
        except Exception, ex:
            self._logger.error('Could not toggle fan' + str(ex))

    def still(self, address, *args, **kwargs):
        self._fan = False
        self.interface.toggle_fan(address[0], address[1])
    
    def occupy(self, address, *args, **kwargs):
        self._away = False
        self.interface.toggle_away(address[0], address[1])

    def vacate(self, address, *args, **kwargs):
        self._away = True
        self.interface.toggle_away(address[0], address[1])

    def level(self, address, level, timeout=2.0):
        self._set_point = level
        try:
            self.interface.change_temperature(address[0], address[1], level)
        except Exception, ex:
            self._logger.error('Error setting temperature' + str(ex))
        return 
    
    def version(self):
        self._logger.info("HW Thermostat Pytomation driver version " + self.VERSION + '\n')
        
    def _process_current_temp(self, response):
        temp = None
        try:
            status = json.loads(response)
            temp = status['temp']
        except Exception, ex:
            self._logger.error('HW Thermostat couldnt decode status json: ' + str(ex))
        if temp and temp != self._last_temp:
            self._onCommand(command=(Command.LEVEL, temp),address=self._host)

    def _process_mode(self, response):
        self._logger.debug("HW - process mode" + str(response))
        mode = response['tmode']
        command = None
        if mode == 0:
            command = Command.OFF
        elif mode == 1:
            command = Command.HEAT
        elif mode == 2:
            command = Command.COOL
        elif mode == 3:
            command = Command.SCHEDULE
        self._logger.debug('HW Status mode = ' + str(command))
        if command != self._mode:
            self._mode = command
            self._onCommand(command=command,address=self._host)
        
