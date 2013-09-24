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
        self._hold = None
        self._fan = None
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
                    status = []
                    try:
                        status = json.loads(response)
                    except Exception, ex:
                        self._logger.error('Could not decode status request' + str(ex))
                    self._process_mode(status)
        else:
            self._iteration+=1
            time.sleep(1) # one sec iteration
    
    def heat(self, *args, **kwargs):
        self._mode = Command.HEAT
        return self._send_state()

    def cool(self, *args, **kwargs):
        self._mode = Command.COOL
        return self._send_state()

    def schedule(self, *args, **kwargs):
        self._mode = Command.SCHEDULE
        self._hold = False
        return self._send_state()

    def hold(self, *args, **kwargs):
        self._hold = True
        return self._send_state()

    def circulate(self, *args, **kwargs):
        self._fan = True
        return self._send_state()

    def still(self, *args, **kwargs):
        self._fan = False
        return self._send_state()
    
    def off(self, *args, **kwargs):
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
            
        

    def _send_state(self):
        modes = dict(zip([Command.OFF, Command.HEAT, Command.COOL, Command.SCHEDULE],
                         range(0,4)))
        try:
            attributes = {}
            if self._set_point <> None:
                if self._mode == Command.HEAT or self._mode == None:
                    attributes['t_heat'] = self._set_point
                elif self._mode == Command.COOL:
                    attributes['t_cool'] = self._set_point
            if self._fan <> None:
                attributes['fmode'] = 2 if self._fan else 1
            if self._mode <> None:
                attributes['tmode'] = modes[self._mode]
            if self._hold <> None:
                attributes['hold'] = 1 if self._hold or self._mode != Command.SCHEDULE else 0
                
            command = ('tstat', json.dumps(attributes)
                    )
        except Exception, ex:
            self._logger.error('Could not formulate command to send: ' + str(ex))

        commandExecutionDetails = self._sendInterfaceCommand(command)
        return True
        #return self._waitForCommandToFinish(commandExecutionDetails, timeout=2.0)
        