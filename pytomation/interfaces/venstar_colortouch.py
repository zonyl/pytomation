"""
Venstar Colortouch thermostat Pytomation Interface

Author(s):
David Heaps - king.dopey.10111@gmail.com

reuse from:
Jason Sharpee

which was reused from:
 George Farris <farrisg@gmsys.com>
"""

import json,urllib,time

from .ha_interface import HAInterface
from .common import Interface, Command

class VenstarThermostat(HAInterface):
    VERSION = '1.0.1'

    def _init(self, *args, **kwargs):
        super(VenstarThermostat, self)._init(*args, **kwargs)
        self._last_temp = None
        self._CoolSetpoint = None
        self._HeatSetpoint = None
        self._set_point = None
        self._last_set_point = None
        self._mode = None
        self._fan = None
        self._last_state = None
        self._schedule = None
        self._away = None
        self._SetPointDelta = None

        responses = self._interface.read()
        self._logger.debug("[Venstar Thermostat] API> " + str(responses))
        if json.loads(responses)['type'] == "commercial":
            self._away_type = "holiday"
        else:
            self._away_type = "away"

        self._iteration = 0
        #the delay to poll the thermostat
        self._poll_secs = kwargs.get('poll', 60)

        try:
            self._host = self._interface.host
        except Exception, ex:
            self._logger.debug('[Venstar Thermostat] Could not find host address: ' + str(ex))


    def _process_current_temp(self, response):
        temp = None
        try:
            status = json.loads(response)

        except Exception, ex:
            self._logger.error("Venstar Thermostat couldn't decode status json: " + str(ex))


    def _process_mode(self, response):
        self._logger.debug("Venstar - process mode" + str(response))


    def _readInterface(self, lastPacketHash):
        # We need to dial back how often we check the thermostat.. Lets not bombard it!
        if not self._iteration < self._poll_secs:
            self._iteration = 0
            #check to see if there is anything we need to read
            responses = self._interface.read('query/info')
            if len(responses) != 0:
                status = []
                try:
                    status = json.loads(responses)
                    self._logger.debug("[Venstar Thermostat] Response> " + str(responses))
                    mode = status['mode']
                    command = None
                    state = status['state']
                    self._away = status['holiday']
                    self._schedule = status['schedule']
                    self._CoolSetpoint = status['cooltemp']
                    self._HeatSetpoint = status['heattemp']
                    self._SetPointDelta = status['setpointdelta']
                    if state == 1 or state == 2: self._last_state = state
                    if mode == 0:
                        command = Command.OFF
                    elif mode == 1:
                        command = Command.HEAT
                        self._set_point = self._HeatSetpoint
                        self._last_state = mode
                    elif mode == 2:
                        command = Command.COOL
                        self._set_point = self._CoolSetpoint
                        self._last_state = mode
                    elif mode == 3:
                        command = Command.AUTOMATIC
                        if self._last_state:
                            if self._last_state==1: #heating
                                self._set_point = self._HeatSetpoint
                            elif self._last_state==2: #cooling
                                self._set_point = self._CoolSetpoint
                        else: #hasn't turned on yet, try and guess
                            if self._last_temp > self._CoolSetpoint:
                                self._set_point = self._CoolSetpoint
                            if self._last_temp < self._HeatSetpoint:
                                self._set_point = self._CoolSetpoint
                            else:
                                self._set_point = self._HeatSetpoint

                    self._logger.debug('Venstar Status mode = ' + str(command))

                    if self._set_point != self._last_set_point:
                        self._last_set_point = self._set_point
                        self._onCommand(command=(Command.SETPOINT, self._set_point))

                    if command != self._mode:
                        self._mode = command
                        self._onCommand(command=command)

                    temp = status['spacetemp']
                    if temp and temp != self._last_temp:
                        self._onCommand(command=(Command.LEVEL, temp))
                        self._last_temp = temp

                    fan = status['fan']
                    if fan and int(fan) != self._fan:
                        _fan = int(fan)

                except Exception, ex:
                    self._logger.error('Could not decode status request' + str(ex))
            else:
                self._logger.debug("No response")
        else:
            self._iteration+=1
            time.sleep(1) # one sec iteration
            
    def _writeInterfaceFinal(self, data):
        return self._interface.read(data)

    def _send_state(self):
        modes = dict(zip([Command.OFF, Command.HEAT, Command.COOL, Command.AUTOMATIC],
                         range(0,4)))
        try:
            attributes = {}
            if self._mode <> None:
                attributes['mode'] = modes[self._mode]
            if self._fan <> None:
                attributes['fan'] = 1 if self._fan else 0
            if self._set_point <> None:
                    attributes['heattemp'] = self._HeatSetpoint
                    attributes['cooltemp'] = self._CoolSetpoint

            command = ('control', urllib.urlencode(attributes),)
        except Exception, ex:
            self._logger.error('Could not formulate command to send: ' + str(ex))

        commandExecutionDetails = self._sendInterfaceCommand(command)
        return True

    def send_settings(self):
        try:

            attributes = {
              'tempunits': 0, #0 - Fahrenheit; 1 - Celsius
              self._away_type: self._away,
              'schedule': self._schedule
            }
            command = ('settings', urllib.urlencode(attributes),)
        except:
            self._logger.error('Could not formulate command to send: ' + str(ex))

        commandExecutionDetails = self._sendInterfaceCommand(command)
        return True

    def warmer(self):
        self._last_set_point = self._set_point
        self._set_point += 1
        self._CoolSetpoint += 1
        self._HeatSetpoint += 1
        return self._send_state()
    
    def cooler(self):
        self._last_set_point = self._set_point
        self._set_point -= 1
        self._CoolSetpoint -= 1
        self._HeatSetpoint -= 1
        return self._send_state()
    
    def heat(self, *args, **kwargs):
        self._mode = Command.HEAT
        self._last_state = 1
        return self._send_state()

    def cool(self, *args, **kwargs):
        self._mode = Command.COOL
        self._last_state = 2
        return self._send_state()

    def automatic(self, *args, **kwargs):
        self._mode = Command.AUTOMATIC
        return self._send_state()

    def schedule(self, *args, **kwargs):
        self._schedule = 1
        return self.send_settings()

    def hold(self, *args, **kwargs):
        self._schedule = 0
        return self.send_settings()

    def vacate(self, *args, **kwargs):
        self._away = 1
        return self.send_settings()

    def occupy(self, *args, **kwargs):
        self._away = 0
        return self.send_settings()

    def circulate(self, *args, **kwargs):
        self._fan = True
        return self._send_state()

    def still(self, *args, **kwargs):
        self._fan = False
        return self._send_state()

    def off(self, *args, **kwargs):
        self._mode = Command.OFF
        return self._send_state()

    def setpoint(self, address, level, timeout=2.0):
        setpoint_change = level - self._set_point
        self._set_point = level
        if self._last_state == 1:
            self._HeatSetpoint = level
            self._CoolSetpoint = level + self._SetPointDelta
        elif self._last_state == 2:
            self._CoolSetpoint = level
            self._HeatSetpoint = level - self._SetPointDelta
        else:
            self._CoolSetpoint += setpoint_change
            self._HeatSetpoint += setpoint_change
        return self._send_state()

    def version(self):
        self._logger.info("Venstar Thermostat Pytomation driver version " + self.VERSION + '\n')