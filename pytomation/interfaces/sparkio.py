"""
Spark IO devices interface driver
https://www.spark.io/

Protocol Docs:
http://docs.sparkdevices.com/

Essentially the Device is a simple REST interface. Kudos to them for making a straightforward and simple API!

Author(s):
Jason Sharpee
jason@sharpee.com

"""
import json
import re
import time
import urllib

from .ha_interface import HAInterface
from .common import *

class SparkIO(HAInterface):
    VERSION = '1.0.0'
    
    def _init(self, *args, **kwargs):
        super(SparkIO, self)._init(*args, **kwargs)
        self._iteration = 0
        self._poll_secs = kwargs.get('poll', 60)

        try:
            self._host = self._interface.host
        except Exception, ex:
            self._logger.debug('Could not find host address: ' + str(ex))
        
    def _readInterface(self, lastPacketHash):
        # We need to dial back how often we check the thermostat.. Lets not bombard it!
        if not self._iteration < self._poll_secs:
            self._iteration = 0
            #check to see if there is anything we need to read
            responses = self._interface.read('v1/:id/events')
            if len(responses) != 0:
                for response in responses.split():
                    self._logger.debug("[Spark Devices] Response> " + hex_dump(response))
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
    
    def version(self):
        self._logger.info("SparkIO Devices Pytomation driver version " + self.VERSION + '\n')
    
    def on(self, address=None, timeout=None, *args, **kwargs):
        return self._set_pin(address, Command.ON, timeout=timeout)
    
    def off(self, address=None, timeout=None, *args, **kwargs):
        return self._set_pin(address, Command.ON, timeout=timeout)

    def _set_pin(self, address, command, timeout=2.0):
        pin_state = {
                     Command.ON: 'HIGH',
                     Command.OFF: 'LOW',
                     }
        url = ('v1/devices/' + address[0])
        attributes = {}
        attributes['pin'] = address[1]
        attributes['level'] = pin_state[command]

#        command = (url, json.dumps(attributes))
        command = (url, urllib.urlencode(attributes))
        
        commandExecutionDetails = self._sendInterfaceCommand(command)
        return True

        #return self._waitForCommandToFinish(commandExecutionDetails, timeout=2.0)
                   
        