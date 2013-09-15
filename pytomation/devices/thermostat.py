from pytomation.devices import InterfaceDevice, State
from pytomation.interfaces import Command

class Thermostat(InterfaceDevice):
    STATES = [State.UNKNOWN, State.OFF, State.HEAT, State.COOL, State.LEVEL, State.CIRCULATE, State.AUTOMATIC]
    COMMANDS = [Command.AUTOMATIC, Command.COOL, Command.HEAT, Command.HOLD, Command.SCHEDULE, Command.OFF, Command.LEVEL, Command.STATUS, Command.CIRCULATE, Command.STILL]

    _level = None
    _setpoint = None
    _automatic = False
    
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
                self._automatic = True
                self.automatic_check()
    
    def automatic_check(self):
        if self._automatic:
            if isinstance(self._state, tuple) and self._state[0] == State.LEVEL and self._state[1] != self._setpoint:
                if self._state[1] < self._setpoint:
                    self.heat(address=self._address, source=self)
                else:
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
        
        if primary_command == State.LEVEL and (source != self or not source) and source not in self._interfaces:
            self._setpoint = secondary_command

        result = super(Thermostat, self).command(command, *args, **kwargs)
        
        self.automatic_check()
        return result