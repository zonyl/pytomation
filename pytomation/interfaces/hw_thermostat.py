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
        self._iteration = 0
        self._poll_secs = kwargs.get('poll', 60)

        try:
            self._host = self._interface.host
        except Exception, ex:
            self.logger.debug('[HW Thermostat] Could not find host address: ' + str(ex))
        
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
        command = ('tstat', json.dumps({'tmode': 1}))
        commandExecutionDetails = self._sendInterfaceCommand(command)
#        return self._waitForCommandToFinish(commandExecutionDetails, timeout=2.0)

    def cool(self, address):
        command = ('tstat', json.dumps({'tmode': 2}))
        commandExecutionDetails = self._sendInterfaceCommand(command)
#        return self._waitForCommandToFinish(commandExecutionDetails, timeout=2.0)

    def run(self, address):
        command = ('tstat', json.dumps({'tmode': 3, 'hold': 0}))
        commandExecutionDetails = self._sendInterfaceCommand(command)
#        return self._waitForCommandToFinish(commandExecutionDetails, timeout=2.0)

    def hold(self, address):
        command = ('tstat', json.dumps({'hold': 1}))
        commandExecutionDetails = self._sendInterfaceCommand(command)
#        return self._waitForCommandToFinish(commandExecutionDetails, timeout=2.0)
                 
    def circulate(self, address):
        command = ('tstat', json.dumps({'fmode': 2}))
        commandExecutionDetails = self._sendInterfaceCommand(command)
#        return self._waitForCommandToFinish(commandExecutionDetails, timeout=2.0)

    def still(self, address):
        command = ('tstat', json.dumps({'fmode': 0}))
        commandExecutionDetails = self._sendInterfaceCommand(command)
#        return self._waitForCommandToFinish(commandExecutionDetails, timeout=2.0)

    def off(self, address):
        command = ('tstat', json.dumps({'fmode': 0, 'tmode': 0}))
        commandExecutionDetails = self._sendInterfaceCommand(command)
#        return self._waitForCommandToFinish(commandExecutionDetails, timeout=2.0)
    
    def level(self, address, level):
        command = ('tstat', json.dumps({'t_heat': level, 't_cool': level}))
        commandExecutionDetails = self._sendInterfaceCommand(command)
#        return self._waitForCommandToFinish(commandExecutionDetails, timeout=2.0)
    
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
        