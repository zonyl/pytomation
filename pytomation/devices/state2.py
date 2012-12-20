from ..common import PytomationObject
from ..interfaces import Command

class State2(object):
    UNKNOWN = 'unknown'
    ON = 'on'
    OFF = 'off'
    LEVEL = 'level'
    
class State2Device(PytomationObject):
    STATES = [State2.UNKNOWN, State2.ON, State2.OFF, State2.LEVEL]
    COMMANDS = [Command.ON, Command.OFF, Command.LEVEL]
    
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
            return lambda *a, **k: self.command(name, *a, sub_state=a, **k)

    def command(self, command, *args, **kwargs):
        state = self._command_state_map(command, *args, **kwargs)
        if state and self._is_valid_state(state):
            self.state = state

    def _command_state_map(self, command, *args, **kwargs):
        if command == Command.ON:
            state = State2.ON
        elif command == Command.OFF:
            state = State2.OFF
        elif command == Command.LEVEL:
            state = (State2.LEVEL, kwargs.get('sub_state', (0,))[0])
        return state

    def _process_kwargs(self, kwargs):
        # Process each initializing attribute as a method call on this object
        for k, v in kwargs.iteritems():
            getattr(self, k)(v)
            
    def _is_valid_state(self, state):
        isFound = state in self.STATES
        if not isFound:
            try:
                isFound = state[0] in self.STATES
            except:
                pass
        return isFound

    def _is_valid_command(self, command):
        return command in self.COMMANDS

    def initial(self, state):
        self.state = state