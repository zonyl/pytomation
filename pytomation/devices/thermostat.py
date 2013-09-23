from pytomation.devices import InterfaceDevice, State
from pytomation.interfaces import Command

class Thermostat(InterfaceDevice):
    STATES = [State.UNKNOWN, State.OFF, State.HEAT, State.COOL, State.LEVEL, State.CIRCULATE, State.AUTOMATIC, State.HOLD]
    COMMANDS = [Command.AUTOMATIC, Command.MANUAL, Command.COOL, Command.HEAT, Command.HOLD, Command.SCHEDULE, Command.OFF, Command.LEVEL, Command.STATUS, Command.CIRCULATE, Command.STILL,]

    _level = None
    _setpoint = None
    _automatic_mode = False
    _current_mode = None
    _automatic_delta = 0
    _last_temp = None
    
    def __init__(self, *args, **kwargs):
        for level in range(32,100):
            self.COMMANDS.append((Command.LEVEL, level))
            
        super(Thermostat, self).__init__(*args, **kwargs)
    
    def _send_command_to_interface(self, interface, address, command):
        try:
            super(Thermostat, self)._send_command_to_interface(interface, address, command)
        except AttributeError, ex:
            if command == Command.AUTOMATIC:
                #Thermostat doesnt have Automatic mode
                self._automatic_mode = True
                self.automatic_check()
    
    def automatic_check(self):
        if self._automatic_mode:
            if self._state and self._setpoint and isinstance(self._state, tuple) and self._state[0] == State.LEVEL and self._state[1] != self._setpoint:
                previous_temp = self._state[1]
                if self._state[1] < (self._setpoint - self._automatic_delta):
                    # If the current mode isnt already heat or for some wild reason we are heading in the wrong dir
                    if self._current_mode != Command.HEAT or (self._last_temp and self._last_temp > self._state[1]):
                        self.heat(address=self._address, source=self)
                elif self._state[1] > self._setpoint + self._automatic_delta:
                    # If the current mode isnt already cool or for some wild reason we are heading in the wrong dir
                    if self._current_mode != Command.COOL or (self._last_temp and self._last_temp < self._state[1]):
                        self.cool(address=self._address, source=self)
                self._last_temp = previous_temp

    def command(self, command, *args, **kwargs):
        source = kwargs.get('source', None)
        primary_command = command
        secondary_command = None
        if len(args) > 0:
            secondary_command=args[0]

        if isinstance(primary_command, tuple):
            primary_command=command[0]
            secondary_command=command[1]
        
        if primary_command == Command.LEVEL and \
            (source != self or not source) and \
            source not in self._interfaces:
            self._setpoint = secondary_command

        if primary_command == Command.HEAT:
            self._current_mode = Command.HEAT
        elif primary_command == Command.COOL:
            self._current_mode = Command.COOL
        elif primary_command == Command.OFF:
            self._currect_mode = Command.OFF
        elif primary_command == Command.AUTOMATIC:
            self._automatic_mode = True
        elif primary_command == Command.MANUAL:
            self._automatic_mode = False
        
        result = super(Thermostat, self).command(command, *args, **kwargs)
        
        self.automatic_check()
        return result
        
    def automatic_delta(self, value):
        self._automatic_delta = value
        