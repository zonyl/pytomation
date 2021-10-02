"""
Tomato Router Interface

Author(s):
Jason Sharpee
jason@sharpee.com

"""
import json
import re
import time

from .ha_interface import HAInterface
from .common import *

class TomatoInterface(HAInterface):
    VERSION = '1.0.0'
    
    def _init(self, *args, **kwargs):
        self._user = kwargs.get('user', None)
        self._password = kwargs.get('password', None)
        self._http_id = kwargs.get('http_id', None)
        self._iteration = 0;
        self._poll_secs = 60;

        super(TomatoInterface, self)._init(*args, **kwargs)
        
        try:
            self._host = self._interface.host
        except Exception, ex:
            self._logger.debug('Could not find host address: ' + str(ex))

        
    def _readInterface(self, lastPacketHash):
        # We need to dial back how often we check the thermostat.. Lets not bombard it!
        if not self._iteration < self._poll_secs:
            self._iteration = 0
            #check to see if there is anything we need to read
#             responses = self._interface.read('tstat')
#             if len(responses) != 0:
#                 for response in responses.split():
#                     self._logger.debug("[HW Thermostat] Response> " + hex_dump(response))
#                     self._process_current_temp(response)
#                     status = []
#                     try:
#                         status = json.loads(response)
#                     except Exception, ex:
#                         self._logger.error('Could not decode status request' + str(ex))
#                     self._process_mode(status)
        else:
            self._iteration+=1
            time.sleep(1) # one sec iteration
    
    def restriction(self, *args, **kwargs):
        """
_nextpage:restrict.asp
_service:restrict-restart
rrule1:1|-1|-1|127|192.168.13.119>192.168.13.202|||0|Roku
f_enabled:on
f_desc:Roku
f_sched_allday:on
f_sched_everyday:on
f_sched_begin:0
f_sched_end:0
f_sched_sun:on
f_sched_mon:on
f_sched_tue:on
f_sched_wed:on
f_sched_thu:on
f_sched_fri:on
f_sched_sat:on
f_type:on
f_comp_all:1
f_block_all:on
f_block_http:
_http_id:
"""
        print str(args) + ":" + str(kwargs)
        fdata = {
                "f_desc": args[0],
                "f_enabled": "On" if args[1] else "Off",
                "_http_id": self._http_id,
                }
#        self._sendInterfaceCommand("tomato.cgi", fdata)
        response = self._interface.write(path="tomato.cgi", data=fdata, verb="POST")
        self._logger.debug("Response:" + str(response))       
    
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
        command = Command.ON
        self._onCommand(command=command,address=self._host)
        
    def _send_state(self):
        command = Command.ON
        commandExecutionDetails = self._sendInterfaceCommand(command)
        return True
        #return self._waitForCommandToFinish(commandExecutionDetails, timeout=2.0)
        