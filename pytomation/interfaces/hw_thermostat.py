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
    
    def _readInterface(self, lastPacketHash):
        #check to see if there is anyting we need to read
        responses = self._interface.read('tstat')
        if len(responses) != 0:
            for response in responses.split():
                self._logger.debug("[HW Thermostat] Response> " + hex_dump(response))
                 
        else:
            time.sleep(0.1)  # try not to adjust this 
                 
    def circulate(self, address):
        command = ('tstat', json.dumps({'fmode': 2}), 'POST')
        commandExecutionDetails = self._sendInterfaceCommand(command)
#        return self._waitForCommandToFinish(commandExecutionDetails, timeout=2.0)

    def off(self, address):
        command = ('tstat', json.dumps({'fmode': 0, 'tmode': 0}), 'POST')
        commandExecutionDetails = self._sendInterfaceCommand(command)
#        return self._waitForCommandToFinish(commandExecutionDetails, timeout=2.0)
    
    def level(self, address, level, timeout=None, rate=None):
        pass
    
    def version(self):
        self._logger.info("HW Thermostat Pytomation driver version " + self.VERSION + '\n')