from ..common import PytomationObject
from ..interfaces import Command

class State2(object):
    ON = 'on'
    OFF = 'off'
    UNKNOWN = 'unknown'
    
    
class State2Device(PytomationObject):
    STATES = {
              State2.UNKNOWN: [],
              State2.ON: [Command.ON,],
              State2.OFF: [Command.OFF],
              }
    
    def __init__(self, *args, **kwargs):
        super(State2Device, self).__init__(*args, **kwargs)
        self._state = State2.UNKNOWN
        self._process_kwargs(kwargs)
        
    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = value
        return self._state
    
    def __getattr__(self, name):
        # Give this object methods for each command supported
        if self._is_valid_command(name):
            return lambda *a, **k: self.command(name, *a, **k)

    def command(self, command, *args, **kwargs):
        state = self._command_state_map(command, *args, **kwargs)
        if state and self._is_valid_state(state):
            self.state = state

    def _command_state_map(self, command, *args, **kwargs):
        if command == Command.ON:
            state = State2.ON
        elif command == Command.OFF:
            state = State2.OFF
        return state

    def _process_kwargs(self, kwargs):
        # Process each initializing attribute as a method call on this object
        for k, v in kwargs.iteritems():
            getattr(self, k)(v)
            
    def _is_valid_state(self, state):
        return state in self.STATES.keys()
    
    def _commands_supported(self):
        supported_commands = []
        for state, command_group in self.STATES.iteritems():
            for command in command_group:
                if command not in supported_commands:
                    supported_commands.append(command)
        return supported_commands

    def _is_valid_command(self, command):
        return command in self._commands_supported()

    def initial(self, state):
        self.state = state