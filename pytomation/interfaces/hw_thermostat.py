"""
Homewerks Radio Thermostat CT-30-H-K2 Wireless Thermostat with Wi-Fi Module, Dual Wireless Inputs and Touch Screen
http://www.amazon.com/gp/product/B004YZFU1Q/ref=oh_details_o01_s00_i00?ie=UTF8&psc=1

Protocol Docs:
http://radiothermostat.com/documents/RTCOA%20WiFI%20API%20V1_0R3.pdf

Essentially the Device is a simple REST interface. Kudos to them for making a straightforward and simple API!

Author(s):
Jason Sharpee
jason@sharpee.com

reuse from:
 George Farris <farrisg@gmsys.com>
"""
import json
import re
import time

from .ha_interface import HAInterface
from .common import *

class HW_Thermostat(HAInterface):
    VERSION = '1.0.0'
    
    def _init(self, *args, **kwargs):
        super(HW_Thermostat, self)._init(*args, **kwargs)
        self._last_temp = None
        self._mode = None
        self._hold = False
        self._fan = False
        self._set_point = None
        
        self._iteration = 0
        self._poll_secs = kwargs.get('poll', 60)

        try:
            self._host = self._interface.host
        except Exception, ex:
            self._logger.debug('[HW Thermostat] Could not find host address: ' + str(ex))
        
    def _readInterface(self, lastPacketHash):
        # We need to dial back how often we check the thermostat.. Lets not bombard it!
        if not self._iteration < self._poll_secs:
            self._iteration = 0
            #check to see if there is anyting we need to read
            responses = self._interface.read('tstat')
            if len(responses) != 0:
                for response in responses.split():
                    self._logger.debug("[HW Thermostat] Response> " + hex_dump(response))
                    self._process_current_temp(response)
        else:
            self._iteration+=1
            time.sleep(1) # one sec iteration
    
    def heat(self, address):
        self._mode = Command.HEAT
        return self._send_state()

    def cool(self, address):
        self._mode = Command.COOL
        return self._send_state()

    def schedule(self, address):
        self._mode = Command.SCHEDULE
        self._hold = False
        return self._send_state()

    def hold(self, address):
        self._hold = True
        return self._send_state()

    def circulate(self, address):
        self._fan = True
        return self._send_state()

    def still(self, address):
        self._fan = False
        return self._send_state()
    
    def off(self, address):
        self._mode = Command.OFF
        return self._send_state()
    
    def level(self, address, level, timeout=2.0):
        self._set_point = level
        return self._send_state()
    
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

    def _send_state(self):
        modes = dict(zip([Command.OFF, Command.COOL, Command.HEAT, Command.SCHEDULE],
                         range(0,4)))
        command = ('tstat', json.dumps({
                                        't_heat': self._set_point, 
                                        't_cool': self._set_point,
                                        'fmode': 1 if self._fan else 0,
                                        'tmode': modes[self._mode],
                                        'hold': 1 if self._hold or self._mode != Command.SCHEDULE else 0,
                                        })
                   )
        commandExecutionDetails = self._sendInterfaceCommand(command)
        return True
        #return self._waitForCommandToFinish(commandExecutionDetails, timeout=2.0)
        