from pytomation.devices import InterfaceDevice, State
from pytomation.interfaces import Command

class Thermostat(InterfaceDevice):
    STATES = [State.UNKNOWN, State.OFF, State.HEAT, State.COOL, State.LEVEL, State.CIRCULATE, State.AUTOMATIC]
    COMMANDS = [Command.AUTOMATIC, Command.COOL, Command.HEAT, Command.HOLD, Command.SCHEDULE, Command.OFF, Command.LEVEL, Command.STATUS, Command.CIRCULATE, Command.STILL]

    _level = None
    _setpoint = None
    _automatic_mode = False
    _current_mode = None
    _automatic_delta = 0
    
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
            if self._state and \
                self._setpoint and \
                isinstance(self._state, tuple) and \
                self._state[0] == State.LEVEL and \
                self._state[1] != self._setpoint:
                if self._state[1] < (self._setpoint - self._automatic_delta) and self._current_mode != Command.HEAT:
                    self.heat(address=self._address, source=self)
                elif self._state[1] > self._setpoint + self._automatic_delta and self._current_mode != Command.COOL:
                    self.cool(address=self._address, source=self)

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
        
        result = super(Thermostat, self).command(command, *args, **kwargs)
        
        self.automatic_check()
        return result
    
    def automatic(self, *args, **kwargs):
        if args and args[0]:
            self._automatic_mode = True

        super(Thermostat, self).automatic(*args, **kwargs)
    
    def automatic_delta(self, value):
        self._automatic_delta = value
        